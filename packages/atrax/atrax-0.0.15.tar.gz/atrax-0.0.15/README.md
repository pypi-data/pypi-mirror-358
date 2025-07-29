# 🕷️ Atrax

![logo](images/logo.png)

Atrax is a lightweight, educational Python library for data manipulation, inspired by pandas. It's designed for developers, students, and data enthusiasts who want to learn, customize, or extend core DataFrame and Series functionality without the overhead of a full-scale framework.

📚 **Documentation**  
Ctrl-click to open in a new tab
View the full docs here: [https://c5m7b4.github.io/atrax/](https://C5m7b4.github.io/atrax/)


### 🚀 What is Atrax?
Atrax is:

- A simplified reimagining of the pandas library.

- Built from scratch in pure Python.

- Easy to read, modify, and extend.

- Focused on core functionality like:

    - Series and DataFrame objects

    - operations like qcut, rank, rolling, resample, and more

    - intuitive data access and slicing

- Great for learning how data libraries work under the hood.

🎯 Why Use Atrax?
- 🧠 Educational: Understand how high-level data operations are implemented from scratch.

- 🧰 Customizable: Build your own behavior or tweak it for niche use cases.

- ⚡ Lightweight: No C extensions, no dependencies.

- 🧪 Test-driven: Designed with testability and correctness in mind.

### Testing

To run tests:

```
pytest
```

To view the coverage run

```
start htmlcov/index.html

```

to build
```
python -m build
```

to publish
```
python -m twine upload dist/*
```

to build the docs
```
pdoc atrax --output-dir docs
```

to view the docs
```
docs/index.html
```