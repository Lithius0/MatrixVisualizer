# port of bindings/imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_full.cpp
from imgui_bundle import imgui, nanovg as nvg, hello_imgui, ImVec2, ImVec4
from nvg_render import NvgTest
from glm import mat2x2


nvg_imgui = nvg.nvg_imgui


class AppState:
    myNvgDemo: NvgTest
    vg: nvg.Context
    myFrameBuffer: nvg_imgui.NvgFramebuffer
    clear_color: list[float]
    display_in_frame_buffer: bool = False

    def __init__(self):
        self.clear_color = [0, 0, 0, 1]


def main():
    app_state = AppState()

    runner_params = hello_imgui.RunnerParams()
    runner_params.imgui_window_params.default_imgui_window_type = hello_imgui.DefaultImGuiWindowType.no_default_window
    runner_params.app_window_params.window_geometry.size = (1200, 600)

    def post_init():
        app_state.vg = nvg_imgui.create_nvg_context_hello_imgui(
            nvg_imgui.NvgCreateFlags.antialias.value | nvg_imgui.NvgCreateFlags.stencil_strokes.value)
        app_state.myNvgDemo = NvgTest(app_state.vg)
        nvg_image_flags = 0
        app_state.myFrameBuffer = nvg_imgui.NvgFramebuffer(
            app_state.vg, 1000, 600, nvg_image_flags)

    def before_exit():
        app_state.myNvgDemo.reset()
        app_state.myFrameBuffer = None
        nvg_imgui.delete_nvg_context_hello_imgui(app_state.vg)

    runner_params.callbacks.enqueue_post_init(post_init)
    runner_params.callbacks.enqueue_before_exit(before_exit)

    def nvg_drawing_function(_: nvg.Context, width: float, height: float):
        now = imgui.get_time()
        mouse_pos = ImVec2(
            imgui.get_mouse_pos().x - imgui.get_main_viewport().pos.x,
            imgui.get_mouse_pos().y - imgui.get_main_viewport().pos.y)
        app_state.myNvgDemo.render(width, height)

    def custom_background():
        clear_color_vec4 = ImVec4(*app_state.clear_color)
        nvg_imgui.render_nvg_to_background(
            app_state.vg, nvg_drawing_function, clear_color_vec4)

    runner_params.callbacks.custom_background = custom_background

    def gui():
        imgui.set_next_window_pos(ImVec2(0, 0), imgui.Cond_.appearing.value)
        imgui.begin("My Window!", None,
                    imgui.WindowFlags_.always_auto_resize.value)

        if app_state.display_in_frame_buffer:
            clear_color_vec4 = ImVec4(*app_state.clear_color)
            nvg_imgui.render_nvg_to_frame_buffer(
                app_state.vg, app_state.myFrameBuffer, nvg_drawing_function, clear_color_vec4)
            imgui.image(app_state.myFrameBuffer.texture_id, ImVec2(1000, 600))

        if imgui.begin_table("MatrixEdit", 2, imgui.TableFlags_.no_pad_inner_x | imgui.TableFlags_.borders_inner):
            for i in range(2):
                imgui.table_setup_column(
                    f"Col{i}", imgui.TableColumnFlags_.width_fixed, 200)
            for i in range(2):
                for j in range(2):
                    imgui.table_next_column()
                    imgui.set_next_item_width(-1)
                    _, out = imgui.input_text(
                        f"##{i},{j}", str(app_state.myNvgDemo.matrix[i][j]), imgui.InputTextFlags_.auto_select_all)
                    app_state.myNvgDemo.matrix[i][j] = float(out)

            imgui.end_table()

        if imgui.button("Generate Dots"):
            app_state.myNvgDemo.clear_dots()
            app_state.myNvgDemo.generate_dots(20)

        if imgui.collapsing_header("Dots"):
            for dot in app_state.myNvgDemo.dots:
                imgui.text(f"{dot.x}, {dot.y}")

        imgui.set_next_item_width(hello_imgui.em_size(15))
        _, app_state.clear_color = imgui.color_edit4(
            "Clear Color", app_state.clear_color)
        if imgui.is_item_hovered():
            imgui.set_tooltip("Background color of the drawing")

        imgui.end()

    runner_params.callbacks.show_gui = gui

    runner_params.fps_idling.enable_idling = False

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
