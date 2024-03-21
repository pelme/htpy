from htpy import div, h1


def fib(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


print(
    div[
        h1["Fibonacci!"],
        "fib(20)=",
        lambda: str(fib(20)),
    ]
)
# output: <div><h1>Fibonacci!</h1>fib(12)=6765</div>
