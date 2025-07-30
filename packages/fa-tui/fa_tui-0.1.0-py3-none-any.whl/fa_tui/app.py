import re
from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Static
from textual.containers import Vertical, Horizontal
from textual import events
import subprocess
from pathlib import Path

result_data = {}

class FridaTUI(App):
    CSS = """
    Screen {
        layout: vertical;
        background: $background;
    }
    #mode-label {
        padding: 1;
        text-align: center;
        background: $accent;
        color: $text;
    }
    #js-files, #frida-output {
        width: 100%;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }
    ListView {
        height: 100%;
    }
    Label {
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        # 使用 Horizontal 容器将两组列表并排显示
        yield Horizontal(
            Vertical(
                Static("frida-ps -Uai 输出", classes="title"),
                ListView(id="frida-output")
            ),
            Vertical(
                Static("当前目录中的 JS 文件", classes="title"),
                ListView(id="js-files")
            )
        )
        # 添加一个显示当前模式的标签，提示可按 M 切换
        yield Static("当前模式: spawn (按 M 切换)", id="mode-label")
    def on_mount(self) -> None:
        self.mode = "spawn"  # 默认模式为 spawn，对应 -f
        self.js_files = []
        self.frida_processes = []

        # 加载当前目录下的 JS 文件
        js_files = [f.name for f in Path.cwd().glob("*.js")]
        self.js_files = js_files
        js_list = self.query_one("#js-files", ListView)
        for file in js_files:
            js_list.append(ListItem(Label(file)))

        # 加载 frida-ps -Uai 输出
        try:
            result = subprocess.run(
                ["frida-ps", "-Uai"],
                capture_output=True,
                text=True,
                check=True
            )
            output_lines = result.stdout.splitlines()[2:]  # 跳过前两行
            self.frida_processes = output_lines
            frida_list = self.query_one("#frida-output", ListView)
            for line in output_lines:
                frida_list.append(ListItem(Label(line)))
        except Exception as e:
            self.frida_processes = [f"Error: {e}"]
            frida_list = self.query_one("#frida-output", ListView)
            frida_list.append(ListItem(Label(str(e))))

    async def on_key(self, event: events.Key) -> None:
        # 按 M 键切换模式
        if event.key.lower() == "m":
            self.mode = "attach" if self.mode == "spawn" else "spawn"
            mode_label = self.query_one("#mode-label", Static)
            mode_label.update(f"当前模式: {self.mode} (按 M 切换)")
        # 按 Enter 键选择当前项并退出 TUI
        elif event.key == "enter":
            js_index = self.query_one("#js-files", ListView).index
            frida_index = self.query_one("#frida-output", ListView).index

            js_file = self.js_files[js_index] if js_index is not None and js_index < len(self.js_files) else None
            frida_proc = self.frida_processes[frida_index] if frida_index is not None and frida_index < len(self.frida_processes) else None

            # 将选择结果和当前模式存入全局变量
            result_data["js_file"] = js_file
            result_data["frida_proc"] = frida_proc
            result_data["mode"] = self.mode

            await self.action_quit()

def main():
    FridaTUI().run()

    if result_data:
        js_file = result_data.get("js_file") or ""
        frida_line = result_data.get("frida_proc") or ""
        mode = result_data.get("mode", "spawn")

        parts = frida_line.split()
        pkg = parts[-1] if parts else ""

        if js_file and pkg:
            # 根据模式选择不同参数
            option = "-f" if mode == "spawn" else "-n"
            cmd = f"frida -U {option} {pkg} -l {js_file}"
            print(f"执行命令：{cmd}")
            try:
                subprocess.run(["frida", "-U", option, pkg, "-l", js_file])
            except FileNotFoundError:
                print("找不到 frida 命令，请确认已正确安装并在 PATH 中。")
            except Exception as e:
                print(f"执行失败: {e}")
        else:
            print("无法生成 frida 命令，可能未正确选择 JS 或进程")


if __name__ == "__main__":
    main()