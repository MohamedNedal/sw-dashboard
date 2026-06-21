"""HUXt CME panel: configure and run a heliospheric simulation.

If the optional ``HUXt`` package is installed a full ambient + cone-CME run is
executed.  Otherwise a lightweight kinematic approximation is drawn so the
panel still communicates CME propagation geometry.
"""
from __future__ import annotations

import io

import numpy as np
import streamlit as st

from swdash.data.huxt_model import huxt_available, run_huxt

AU_IN_RSUN = 215.0


def _fig_to_png(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    import matplotlib.pyplot as plt
    plt.close(fig)
    return buf.getvalue()


def _draw_huxt_axes(ax, result: dict, t_index: int, cme_lon: float):
    """Draw a single HUXt time step onto a polar axes; return the QuadMesh."""
    import numpy as np
    lon = result["lon_rad"]      # (n_lon,) radians
    r = result["r_rs"]           # (n_r,) solar radii
    v = result["v_grid"][t_index]
    # HUXt v_grid is (n_radius, n_longitude); transpose if it comes the other way.
    if v.shape == (len(lon), len(r)):
        v = v.T
    # meshgrid (default 'xy') -> arrays of shape (len(r), len(lon)) matching v.
    THETA, RAD = np.meshgrid(lon, r)
    ax.clear()
    mesh = ax.pcolormesh(THETA, RAD, v, cmap="viridis", vmin=300, vmax=800,
                         shading="auto")
    ax.plot(0, AU_IN_RSUN, marker="o", color="#2a7de1", markersize=9, label="Earth")
    ax.plot(np.deg2rad(cme_lon), r.max() * 0.98, marker="^", color="red", markersize=8)
    ax.set_rmax(r.max())
    ax.set_yticklabels([])
    ax.tick_params(colors="white")
    ax.set_title(f"HUXt solar wind speed  ·  t = {result['times_hr'][t_index]:.0f} h",
                 color="white")
    return mesh


def _style_colorbar(fig, mesh, ax):
    import matplotlib.pyplot as plt
    cbar = fig.colorbar(mesh, ax=ax, pad=0.1, shrink=0.7)
    cbar.set_label("Speed (km/s)", color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="white")


def _plot_huxt_frame(result: dict, t_index: int, cme_lon: float) -> bytes:
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(6, 6), facecolor="#0e1117")
    ax = fig.add_subplot(111, projection="polar", facecolor="#0e1117")
    mesh = _draw_huxt_axes(ax, result, t_index, cme_lon)
    _style_colorbar(fig, mesh, ax)
    return _fig_to_png(fig)


def _huxt_animation_html(result: dict, cme_lon: float,
                         max_frames: int = 48, fps: int = 8) -> str:
    """Build an interactive HTML5/JS player (play/pause/replay/step/speed).

    Uses matplotlib's ``to_jshtml`` so no ffmpeg is needed — frames are embedded
    directly. Frames are downsampled to ``max_frames`` to keep the payload light.
    """
    import matplotlib.pyplot as plt
    from matplotlib import animation

    nt = len(result["times_hr"])
    step = max(1, nt // max_frames)
    frames = list(range(0, nt, step))

    # Lower dpi keeps the embedded-frame payload light for fast browser loading.
    fig = plt.figure(figsize=(6, 6), dpi=80, facecolor="#0e1117")
    ax = fig.add_subplot(111, projection="polar", facecolor="#0e1117")
    mesh = _draw_huxt_axes(ax, result, frames[0], cme_lon)
    _style_colorbar(fig, mesh, ax)  # colorbar lives on its own axes; fixed scale

    def _update(t_index):
        _draw_huxt_axes(ax, result, t_index, cme_lon)
        return (ax,)

    anim = animation.FuncAnimation(fig, _update, frames=frames,
                                   interval=1000 / fps, blit=False)
    html = anim.to_jshtml(fps=fps, default_mode="loop")
    plt.close(fig)
    return html


def _plot_kinematic(speed: float, lon: float, width: float, hours: float) -> bytes:
    import matplotlib.pyplot as plt
    r_front = (speed * hours * 3600) / 6.957e5  # km -> solar radii
    theta = np.deg2rad(np.linspace(lon - width / 2, lon + width / 2, 50))

    fig = plt.figure(figsize=(6, 6), facecolor="#0e1117")
    ax = fig.add_subplot(111, projection="polar", facecolor="#0e1117")
    ax.plot(0, AU_IN_RSUN, marker="o", color="#2a7de1", markersize=9, label="Earth")
    ax.plot(theta, [r_front] * len(theta), color="red", lw=3, label="CME front")
    ax.fill_between(theta, 0, r_front, color="red", alpha=0.12)
    ax.plot(0, 0, marker="*", color="#FDB813", markersize=16)
    ax.set_rmax(max(r_front * 1.1, AU_IN_RSUN * 1.2))
    ax.set_yticklabels([])
    ax.tick_params(colors="white")
    ax.set_title(f"Kinematic CME front  ·  t = {hours:.0f} h  ·  {r_front:.0f} R☉",
                 color="white")
    ax.legend(loc="upper right", facecolor="#0e1117", labelcolor="white")
    return _fig_to_png(fig)


def render():
    st.subheader("HUXt — CME Propagation in the Heliosphere")
    have_huxt = huxt_available()
    if have_huxt:
        st.success("HUXt is installed — full model runs are available.")
    else:
        st.info("HUXt is not installed; showing a kinematic approximation. "
                "Install it for a physical simulation:\n\n"
                "`pip install git+https://github.com/University-of-Reading-Space-Science/HUXt.git`")

    with st.form("huxt_form"):
        c = st.columns(4)
        speed = c[0].number_input("CME speed (km/s)", 300, 3000, 1000, 50)
        lon = c[1].number_input("Longitude (°)", -180, 180, 0, 5)
        width = c[2].number_input("Width (°)", 10, 120, 40, 5)
        simdays = c[3].number_input("Sim time (days)", 1, 10, 5, 1)
        thickness = st.slider("CME thickness (R☉)", 1, 20, 5)
        use_mas = st.checkbox(
            "Use MAS coronal boundary (downloads data; otherwise synthetic stream)",
            value=False, disabled=not have_huxt)
        submitted = st.form_submit_button("Run simulation")

    if submitted:
        if have_huxt:
            with st.spinner("Running HUXt…"):
                try:
                    st.session_state["huxt_result"] = run_huxt(
                        cme_speed=speed, cme_longitude=lon, cme_width=width,
                        cme_thickness=thickness, simtime_days=simdays,
                        use_mas=use_mas,
                    )
                    st.session_state["huxt_cme_lon"] = lon
                    # Invalidate any cached animation from a previous run.
                    st.session_state.pop("huxt_anim_html", None)
                except Exception as exc:  # noqa: BLE001
                    st.error(f"HUXt run failed: {exc}")
        else:
            st.session_state["kin_params"] = dict(speed=speed, lon=lon,
                                                  width=width, simdays=simdays)

    # --- Render results ------------------------------------------------------
    if have_huxt and "huxt_result" in st.session_state:
        import streamlit.components.v1 as components

        result = st.session_state["huxt_result"]
        cme_lon = st.session_state.get("huxt_cme_lon", 0.0)
        nt = len(result["times_hr"])

        view = st.radio("View", ["Animation", "Single step"],
                        horizontal=True, index=0)
        if view == "Animation" and nt > 1:
            if "huxt_anim_html" not in st.session_state:
                with st.spinner("Rendering animation…"):
                    st.session_state["huxt_anim_html"] = _huxt_animation_html(
                        result, cme_lon)
            st.caption("Use the ▶/❚❚ controls below to play, pause, step, loop "
                       "and change speed.")
            components.html(st.session_state["huxt_anim_html"],
                            height=760, scrolling=True)
        else:
            idx = st.slider("Time step", 0, nt - 1, nt - 1,
                            format="%d") if nt > 1 else 0
            st.image(_plot_huxt_frame(result, idx, cme_lon),
                     use_container_width=True)

        arr = result.get("arrival")
        if arr and arr.get("hit"):
            st.success(f"CME impacts Earth — arrival {arr['arrival_time']}, "
                       f"transit {arr['transit_time_days']:.2f} d, "
                       f"speed {arr['arrival_speed']:.0f} km/s")
        elif arr is not None:
            st.info("CME does not hit Earth in this run.")

    elif not have_huxt and "kin_params" in st.session_state:
        p = st.session_state["kin_params"]
        max_h = p["simdays"] * 24
        hours = st.slider("Hours since launch", 1, int(max_h), int(max_h))
        st.image(_plot_kinematic(p["speed"], p["lon"], p["width"], hours),
                 use_container_width=True)
        eta = AU_IN_RSUN * 6.957e5 / p["speed"] / 3600
        st.caption(f"Straight-line Sun→Earth travel time at {p['speed']} km/s ≈ "
                   f"{eta:.1f} h ({eta/24:.2f} days).")
