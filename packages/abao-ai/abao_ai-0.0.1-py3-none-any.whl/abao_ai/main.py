from cuda.bindings.runtime import cudaGetDeviceCount, cudaGetDeviceProperties


def hello():
    _, count = cudaGetDeviceCount()
    for i in range(count):
        _, props = cudaGetDeviceProperties(i)
        name = props.name.decode("utf-8")
        print(name)


if __name__ == "__main__":
    hello()
