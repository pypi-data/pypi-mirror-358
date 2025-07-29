#!/usr/bin/env python

from vsplit import chunk_from_env


def main():
    with chunk_from_env() as fp:
        data = fp.read(10)
        print(f"I read {data!r}.")


if __name__ == "__main__":
    main()
