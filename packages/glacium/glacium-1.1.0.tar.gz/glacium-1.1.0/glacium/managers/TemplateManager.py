"""Wrapper around Jinja2 with shared environment and cache.

Templates are loaded on demand and cached for reuse.  When no loader is
configured a default loader pointing to ``<package>/templates`` is created.

Example
-------
>>> tm = TemplateManager()
>>> tm.render('hello.j2', {'name': 'World'})
'Hello World'
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

from jinja2 import Environment, FileSystemLoader, BaseLoader, Template

__all__ = ["TemplateManager"]

# ---------------------------------------------------------------------------
# Borg Singleton for shared state
# ---------------------------------------------------------------------------
class _SharedState:
    __shared_state: Dict[str, object] = {}
    def __init__(self):
        self.__dict__ = self.__shared_state

# ---------------------------------------------------------------------------
class TemplateManager(_SharedState):
    """Centralised Jinja2 environment with template cache.

    Features
    --------
    * Strategy pattern – loader can be swapped (FS, Dict, …)
    * Flyweight        – template cache keyed by relative path
    * Auto fallback    – if no loader set, uses `<package>/templates`
    """

    def __init__(self, template_root: Path | None = None):
        """Initialise the shared environment optionally pointing to ``template_root``."""

        super().__init__()
        if not getattr(self, "_initialised", False):
            self._cache: Dict[Path, Template] = {}
            self._loader: BaseLoader | None = None
            self._env: Environment | None = None
            self._initialised = True

        if template_root is not None:
            self.set_loader(FileSystemLoader(str(template_root)))

    # ------------------------------------------------------------------
    # Loader handling
    # ------------------------------------------------------------------
    def set_loader(self, loader: BaseLoader):
        """Set a new Jinja ``loader`` and clear the cache."""

        self._loader = loader
        self._env = Environment(loader=self._loader, autoescape=False)
        self._cache.clear()

    def _ensure_loader(self):
        """Create a default loader if none has been configured."""

        if self._env is None:
            default_root = Path(__file__).resolve().parents[1] / "templates"
            self.set_loader(FileSystemLoader(str(default_root)))

    # ------------------------------------------------------------------
    # Template access helpers
    # ------------------------------------------------------------------
    def _get_template(self, rel_path: str | Path) -> Template:
        """Return a compiled template for ``rel_path`` from the cache."""

        self._ensure_loader()
        key = Path(rel_path)
        if key not in self._cache:
            self._cache[key] = self._env.get_template(str(key))  # type: ignore[index]
        return self._cache[key]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render(self, rel_path: str | Path, ctx: dict) -> str:
        """Render template ``rel_path`` with context ``ctx`` and return text."""

        return self._get_template(rel_path).render(**ctx)

    def render_to_file(self, rel_path: str | Path, ctx: dict, dest: Path) -> Path:
        """Render template to ``dest`` and return the written path.

        Example
        -------
        >>> tm.render_to_file('in.txt.j2', {'x': 1}, Path('out.txt'))
        """

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.render(rel_path, ctx), encoding="utf-8")
        return dest

    def render_batch(self, rel_paths: Iterable[str | Path], ctx: dict, out_root: Path):
        """Render many templates, stripping a final `.j2` extension only.

        Example
        -------
        >>> tm.render_batch(['a.j2', 'b.j2'], {}, Path('out'))
        """
        for rel in rel_paths:
            rel_p = Path(rel)
            target_name = rel_p.with_suffix("") if rel_p.suffix == ".j2" else rel_p
            out_file = out_root / target_name
            self.render_to_file(rel_p, ctx, out_file)

    def clear_cache(self):
        """Drop all cached templates.

        Example
        -------
        >>> tm.clear_cache()
        """

        self._cache.clear()

