# README

## run without install

```sh
➜  ~ uvx --from echowuhao hello
Hello from echowuhao!

➜  ~ uv tool list
echowuhao v0.3.4
- auto_commit
- hello
ruff v0.6.4
- ruff
```

### run latest version without install

```sh
uvx  --from echowuhao@latest hello
```

## install and run

```sh
➜  ~ uv tool install echowuhao==0.3.4
Resolved 6 packages in 2.13s
Prepared 1 package in 192ms
Uninstalled 1 package in 7ms
Installed 1 package in 8ms
 - echowuhao==0.2.0 (from file:///Users/hwu/dev/py_lib/echowuhao)
 + echowuhao==0.3.4
Installed 2 executables: auto_commit, hello

➜  ~ uv tool list
echowuhao v0.3.4
- auto_commit
- hello
ruff v0.6.4
- ruff

➜  ~ hello
Hello from echowuhao!
```

### upgrade

```sh
➜  dev uv tool upgrade echowuhao
Updated echowuhao v0.3.6 -> v0.3.7
 - anyio==4.4.0
 + anyio==4.6.0
 - echowuhao==0.3.6
 + echowuhao==0.3.7
 - openai==1.45.0
 + openai==1.47.0
 - pydantic==2.9.1
 + pydantic==2.9.2
 - pydantic-core==2.23.3
 + pydantic-core==2.23.4
Installed 4 executables: auto_commit, chat, choose_model, hello
```

## dev

uv develop and build using uv is good

```sh
uv sync
uv lock
```

```sh
uv build
```

## uploading

```sh
uvx twine upload dist/*
```

## install

### using uv

```sh
uv tool install echowuhao==0.3.4
```

