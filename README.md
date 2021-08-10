# Get and create paths for your app
`app_paths` builds upon [`appdirs`](https://pypi.org/project/appdirs/) and automatically creates canonical file system paths for storing app and user data on Windows, macOS, Linux and *BSD.

Instead of just strings, `app_paths` gives developers `Path` objects from [`pathlib`](https://docs.python.org/3/library/pathlib.html) or [`aiopath`](https://github.com/alexdelorenzo/aiopath), and it handles path creation efficiently. It also adds [async support](https://www.python.org/dev/peps/pep-0492/).

This project uses [`📁 aiopath`](https://github.com/alexdelorenzo/aiopath) as an async [`pathlib`](https://docs.python.org/3/library/pathlib.html) replacement.

## Use case
First, let's take a look at [`appdirs`](https://pypi.org/project/appdirs/):
```python
from pathlib import Path
from appdirs import AppDirs


dirs = AppDirs('app', 'My Name', '0.1.0')

# appdirs will return uncreated paths as strings
user_data: str = dirs.user_data_dir
assert isinstance(user_data, str)

print(user_data)  # '/home/user/.cache/app/0.1.0'
```

`appdirs` can generate paths as strings for an app. It does one thing, and it does that one thing well on multiple platforms.

```python3
user_data_path = Path(user_data)

# appdirs does not create paths
assert not user_data_path.exists()
```

However, it's up to app developers to handle creating paths on users' file systems. It's also up to developers to decide how they want to manipulate those paths, using abstractions like [`os.path`](https://docs.python.org/3/library/os.path.html), [`pathlib`](https://docs.python.org/3/library/pathlib.html) or [`aiopath`](https://github.com/alexdelorenzo/aiopath). Developers also have to think about how to efficiently perform path creation.

`app_paths` takes care of all of that for you.

`app_paths` automatically gives you [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html) handles for your paths in synchronous apps, and [`aiopath.AsyncPath`](https://github.com/alexdelorenzo/aiopath) handles for async apps. 

```python3
from app_paths import AppPaths


paths = AppPaths.get_paths('app', 'My Name', '0.1.0')

# app_paths can return paths
user_data: Path = paths.user_data_path
assert isinstance(user_data, Path)

print(user_data)  # '/home/user/.cache/app/0.1.0'
```

`app_paths` can create paths on the file system dynamically, and it will cache results so excess I/O isn't performed.

```python3
# app_paths can return uncreated paths
assert not user_data.exists()

# but it can also dynamically create paths on the fly
user_data: Path = paths.user_data
assert user_data.exists()
```

It can do batch creation of app paths, and it will use efficient concurrent I/O in both synchronous and async Python programs.

```python3
# create user app paths concurrently
await paths.create_user()

# to run the following you must have write access to all paths
# create site app paths concurrently
await paths.create_site()

# create user and site paths concurrently
await paths.create_all()
```

Here's how you can do the above asynchronously:
```python3
from app_paths import AsyncAppPaths
from aiopath import AsyncPath


paths = await AsyncAppPaths.get_paths('app', 'My Name', '0.1.0')

# app_paths can return AsyncPaths
user_data: AsyncPath = paths.user_data_path
assert isinstance(user_data, AsyncPath)

print(user_data)  # '/home/user/.cache/app/0.1.0'

# app_paths can return uncreated paths
assert not await user_data.exists()

# but it can also dynamically create paths on the fly
user_data: AsyncPath = await paths.user_data
assert await user_data.exists()

# create user app paths concurrently
await paths.create_user()

# to run the following you must have write access to all paths
# create site app paths concurrently
await paths.create_site()

# create user and site paths concurrently
await paths.create_all()
```

# Installation
## Requirements
 - Windows, macOS or a POSIX compatible operating system
 - Python 3.8+

## PyPI
```bash
$ python3 -m pip install app_paths
```

# Support
Want to support this project and [other open-source projects](https://github.com/alexdelorenzo) like it?

<a href="https://www.buymeacoffee.com/alexdelorenzo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60px" style="height: 60px !important;width: 217px !important;max-width:25%" ></a>

# License
See `LICENSE`. If you'd like to use this project with a different license, please get in touch.
