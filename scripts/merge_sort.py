#!/usr/bin/env python3
import sys


def merge(arr, temp, left, mid, right):
    """
    Merge two sorted subarrays:
    arr[left:mid] and arr[mid:right] into arr[left:right]
    using temp as auxiliary storage.
    """
    i = left
    j = mid
    k = left

    while i < mid and j < right:
        if arr[i] <= arr[j]:
            temp[k] = arr[i]
            i += 1
        else:
            temp[k] = arr[j]
            j += 1
        k += 1

    while i < mid:
        temp[k] = arr[i]
        i += 1
        k += 1

    while j < right:
        temp[k] = arr[j]
        j += 1
        k += 1

    # Copy merged section back into original array
    for idx in range(left, right):
        arr[idx] = temp[idx]


def merge_sort_recursive(arr, temp, left, right):
    if right - left <= 1:
        return

    mid = (left + right) // 2
    merge_sort_recursive(arr, temp, left, mid)
    merge_sort_recursive(arr, temp, mid, right)
    merge(arr, temp, left, mid, right)


def merge_sort(arr):
    """
    Sorts arr in-place using merge sort with O(n) extra space.
    """
    temp = [None] * len(arr)
    merge_sort_recursive(arr, temp, 0, len(arr))


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 merge_sort.py input.txt [output.txt]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else None

    # Read lines (strip newline but preserve content)
    with open(input_file, "r") as f:
        lines = [line.rstrip("\n") for line in f]

    # Sort
    merge_sort(lines)

    # Output
    if output_file:
        with open(output_file, "w") as f:
            for line in lines:
                f.write(line + "\n")
    else:
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
