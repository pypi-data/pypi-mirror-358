def round_robin_generator(targets: list[str]):
    while True:
        for target in targets:
            yield target
