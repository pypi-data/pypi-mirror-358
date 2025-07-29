import fused

@fused.udf()
def test(data):
    return data


if __name__ == "__main__":
    fused.run(test,"111",engine="local")

    test.to_fused(test,"111",engine="local")