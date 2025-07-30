```bash
pip install combine-files[all]   # full feature set (tqdm + pathspec)
# or minimal core
pip install combine-files

# basic usage
combine-files . --preview-exts .md .csv -j 4 --progress
```