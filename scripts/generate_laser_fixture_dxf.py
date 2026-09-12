"""Generate the paired DXF geometry for the synthetic laser fixture."""

from __future__ import annotations

from pathlib import Path

import ezdxf


def main() -> int:
    output = Path("fixtures/laser/cut-bracket/source/bracket.dxf")
    output.parent.mkdir(parents=True, exist_ok=True)
    document = ezdxf.new("R2010", setup=True)
    model = document.modelspace()
    model.add_lwpolyline([(5, 5), (65, 5), (65, 45), (5, 45)], close=True)
    model.add_circle((17, 25), 3)
    model.add_circle((53, 25), 3)
    document.header["$INSUNITS"] = 4
    document.saveas(output)
    text = output.read_text(encoding="utf-8")
    output.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
