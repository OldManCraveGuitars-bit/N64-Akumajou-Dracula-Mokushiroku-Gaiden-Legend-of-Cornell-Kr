"""Open the editor, preparing private ROM assets on first use if necessary."""
import tkinter as tk
from tkinter import filedialog,messagebox
from text_codec import ROOT

def main():
    import sys
    if '--apply-bps' in sys.argv:
        from pathlib import Path
        from prepare_project import normalize,EXPECTED
        from bps import apply
        import hashlib
        root=tk.Tk();root.withdraw()
        try:
            i=sys.argv.index('--apply-bps');source=Path(sys.argv[i+1]);patch=Path(sys.argv[i+2])
            original=normalize(source.read_bytes())
            if hashlib.sha1(original).hexdigest()!=EXPECTED:raise ValueError('지원하는 일본판 원본 롬이 아닙니다.')
            output=source.with_name(source.stem+' (Korean).z64')
            result=apply(original,patch.read_bytes());output.write_bytes(result)
            messagebox.showinfo('한글 패치 완료',str(output.resolve()),parent=root)
        except Exception as error:
            messagebox.showerror('한글 패치 실패',str(error),parent=root);root.destroy();raise SystemExit(1)
        root.destroy();return
    if '--build-check' in sys.argv:
        import build,contextlib,io,json
        log=io.StringIO()
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):build.main()
        report=json.loads((ROOT/'analysis/build-report.json').read_text(encoding='utf-8'))
        (ROOT/'build-self-check.json').write_text(json.dumps(dict(sha256=report['rom_sha256'],log=log.getvalue()),ensure_ascii=False),encoding='utf-8')
        return
    root=tk.Tk();root.withdraw()
    if not (ROOT/'work/manifest.json').exists():
        path=filedialog.askopenfilename(parent=root,title='일본판 원본 롬 선택',filetypes=[('N64 ROM','*.n64 *.z64 *.v64'),('모든 파일','*.*')])
        if not path:root.destroy();return
        try:
            from prepare_project import prepare
            prepare(path)
        except Exception as error:
            messagebox.showerror('원본 준비 실패',str(error),parent=root);root.destroy();return
    from text_editor import Editor
    root.deiconify();editor=Editor(root)
    if '--self-check' in sys.argv:
        first=next(s for s in editor.project.segments if editor.project.target(s))
        editor.tree.selection_set(first['id']);editor.selected();root.update_idletasks();root.update()
        assert editor.preview_image.width()>0 and editor.source_preview_image.width()>0 and editor.tree.get_children()
        (ROOT/'editor-self-check.json').write_text(__import__('json').dumps(dict(rows=len(editor.tree.get_children()),stats=editor.project.stats()),ensure_ascii=False),encoding='utf-8')
        root.destroy();return
    root.mainloop()

if __name__=='__main__':main()
