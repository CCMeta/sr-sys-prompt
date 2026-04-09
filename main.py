from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, UndefinedError

app = FastAPI(title="Prompt Service")

env = Environment(
    loader=FileSystemLoader("templates"),
    keep_trailing_newline=True,
    auto_reload=True,
)


class RenderRequest(BaseModel):
    variables: dict = {}


@app.post("/prompts/{template_path:path}")
def render_prompt(template_path: str, req: RenderRequest):
    """渲染业务模板，返回完整提示词"""
    try:
        template = env.get_template(f"{template_path}.j2")
        rendered = template.render(**req.variables)
        return {"prompt": rendered.strip()}
    except TemplateNotFound:
        raise HTTPException(404, detail=f"模板 '{template_path}' 不存在")
    except UndefinedError as e:
        raise HTTPException(422, detail=f"缺少变量: {e}")


@app.post("/prompts")
def list_templates():
    """列出所有模板（按层分组）"""
    all_templates = env.loader.list_templates()

    def by_layer(prefix):
        return [t.replace(".j2", "") for t in all_templates if t.startswith(prefix)]

    return {
        "base": by_layer("base/"),
        "biz": by_layer("biz/"),
        "components": by_layer("components/"),
    }

# index_root
@app.get("/")
def index_root():
    return FileResponse("index.html")
