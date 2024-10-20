# port of bindings/imgui_bundle/demos_cpp/demos_nanovg/demo_nanovg_full.cpp
from imgui_bundle import imgui, nanovg as nvg, hello_imgui, ImVec2, ImVec4
from nvg_render import NvgData
import glm


nvg_imgui = nvg.nvg_imgui


class AppState:
    nvg_data: NvgData
    vg: nvg.Context
    frame_buffer: nvg_imgui.NvgFramebuffer
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
        app_state.nvg_data = NvgData(app_state.vg)
        nvg_image_flags = 0
        app_state.frame_buffer = nvg_imgui.NvgFramebuffer(
            app_state.vg, 1000, 600, nvg_image_flags)

    def before_exit():
        app_state.nvg_data.reset()
        app_state.frame_buffer = None
        nvg_imgui.delete_nvg_context_hello_imgui(app_state.vg)

    runner_params.callbacks.enqueue_post_init(post_init)
    runner_params.callbacks.enqueue_before_exit(before_exit)

    def nvg_drawing_function(_: nvg.Context, width: float, height: float):
        app_state.nvg_data.render(width, height)

    def custom_background():
        clear_color_vec4 = ImVec4(*app_state.clear_color)
        nvg_imgui.render_nvg_to_background(
            app_state.vg, nvg_drawing_function, clear_color_vec4)

    runner_params.callbacks.custom_background = custom_background

    def gui():
        imgui.set_next_window_pos(ImVec2(0, 0), imgui.Cond_.appearing.value)
        imgui.begin("Linear Algebra", None,
                    imgui.WindowFlags_.always_auto_resize.value)

        if app_state.display_in_frame_buffer:
            clear_color_vec4 = ImVec4(*app_state.clear_color)
            nvg_imgui.render_nvg_to_frame_buffer(
                app_state.vg, app_state.frame_buffer, nvg_drawing_function, clear_color_vec4)
            imgui.image(app_state.frame_buffer.texture_id, ImVec2(1000, 600))

        # Matrices and vectors
        if imgui.begin_table("MatrixEdit", 4, imgui.TableFlags_.no_pad_inner_x | imgui.TableFlags_.borders_inner):
            imgui.table_setup_column(
                f"Transform X", imgui.TableColumnFlags_.width_fixed, 100)
            imgui.table_setup_column(
                f"Transform Y", imgui.TableColumnFlags_.width_fixed, 100)
            imgui.table_setup_column(
                f"Input Vector", imgui.TableColumnFlags_.width_fixed, 100)
            imgui.table_setup_column(
                f"Output Vector", imgui.TableColumnFlags_.width_fixed, 100)
            imgui.table_headers_row()

            for i in range(2):
                for j in range(2):
                    imgui.table_next_column()
                    imgui.set_next_item_width(-1)
                    _, out = imgui.input_text(
                        f"##{i},{j}", str(app_state.nvg_data.matrix[i][j]), imgui.InputTextFlags_.auto_select_all)
                    try:
                        app_state.nvg_data.matrix[i][j] = float(out)
                    except ValueError:
                        # If there's a float conversion error just ignore it.
                        pass
                imgui.table_next_column()
                imgui.set_next_item_width(-1)
                _, input = imgui.input_text(
                    f"##inputv{i}", str(app_state.nvg_data.misc_vector[i]), imgui.InputTextFlags_.auto_select_all)
                try:
                    app_state.nvg_data.misc_vector[i] = float(input)
                except ValueError:
                    # If there's a float conversion error just ignore it.
                    pass
                imgui.table_next_column()
                imgui.set_next_item_width(-1)
                imgui.input_text(f"##ouputv{i}", str(
                    (app_state.nvg_data.matrix * app_state.nvg_data.misc_vector)[i]), imgui.InputTextFlags_.read_only)

            imgui.end_table()

        # Draggers for certain transformations
        drag_changed, drag = imgui.drag_float(
            "Drag to rotate!", 0, 0.01, -1, 1, "", imgui.SliderFlags_.no_input)
        if drag_changed:
            rotation = glm.rotate(-drag)
            app_state.nvg_data.matrix = rotation * app_state.nvg_data.matrix

        scale_changed, scale = imgui.drag_float(
            "Drag to scale!", 1, 0.01, 0, 2, "", imgui.SliderFlags_.no_input)
        if scale_changed:
            app_state.nvg_data.matrix = glm.scale(
                glm.vec2(scale)) * app_state.nvg_data.matrix

        imgui.separator_text("Properties")

        imgui.text(f"Determinant: {glm.determinant(
            app_state.nvg_data.matrix)}")

        imgui.separator_text("Commands")

        if imgui.button("Invert"):
            inverted = glm.inverse(app_state.nvg_data.matrix)
            app_state.nvg_data.matrix = inverted

        if imgui.button("Generate Dots"):
            app_state.nvg_data.clear_dots()
            app_state.nvg_data.generate_dots(20)

        if imgui.button("Clear Dots"):
            app_state.nvg_data.clear_dots()

        imgui.spacing()
        imgui.spacing()

        if imgui.button("Reset"):
            app_state.nvg_data.matrix = glm.mat3x3()

        imgui.separator_text("Background")

        imgui.set_next_item_width(hello_imgui.em_size(15))
        _, app_state.clear_color = imgui.color_edit4(
            "Background Color", app_state.clear_color)
        if imgui.is_item_hovered():
            imgui.set_tooltip("Background color of the drawing")

        imgui.end()

    runner_params.callbacks.show_gui = gui

    runner_params.fps_idling.enable_idling = False

    hello_imgui.run(runner_params)


if __name__ == "__main__":
    main()
