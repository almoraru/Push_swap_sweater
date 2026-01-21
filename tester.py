# ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; #
#                                                                              #
#                        ______                                                #
#                     .-"      "-.                                             #
#                    /            \                                            #
#        _          |              |          _                                #
#       ( \         |,  .-.  .-.  ,|         / )                               #
#        > "=._     | )(__/  \__)( |     _.=" <                                #
#       (_/"=._"=._ |/     /\     \| _.="_.="\_)                               #
#              "=._ (_     ^^     _)"_.="                                      #
#                  "=\__|IIIIII|__/="                                          #
#                 _.="| \IIIIII/ |"=._                                         #
#       _     _.="_.="\          /"=._"=._     _                               #
#      ( \_.="_.="     `--------`     "=._"=._/ )                              #
#       > _.="                            "=._ <                               #
#      (_/                                    \_)                              #
#                                                                              #
#      Filename: lol.py                                                        #
#      By: espadara <espadara@pirate.capn.gg>                                  #
#      Created: 2026/01/20 21:01:49 by espadara                                #
#      Updated: 2026/01/20 21:02:43 by espadara                                #
#                                                                              #
# ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; #

#!/usr/bin/env python3

import subprocess
import random
import sys

# --- CONFIGURATION ---
PUSH_SWAP_PATH = "./push_swap"
ERROR_LOG_FILE = "error_log.txt"

def generate_random_numbers(count):
    return random.sample(range(-2147483648, 2147483647), count)

def internal_python_checker(numbers, ops_string):
    a = numbers[:]
    b = []
    ops = ops_string.strip().split('\n')

    if not ops_string.strip():
        if a == sorted(a): return True, "OK"
        else: return False, "Not sorted (No moves)"

    for op in ops:
        op = op.strip()
        if not op: continue

        try:
            if op == "sa":
                if len(a) > 1: a[0], a[1] = a[1], a[0]
            elif op == "sb":
                if len(b) > 1: b[0], b[1] = b[1], b[0]
            elif op == "ss":
                if len(a) > 1: a[0], a[1] = a[1], a[0]
                if len(b) > 1: b[0], b[1] = b[1], b[0]
            elif op == "pa":
                if b: a.insert(0, b.pop(0))
            elif op == "pb":
                if a: b.insert(0, a.pop(0))
            elif op == "ra":
                if len(a) > 1: a.append(a.pop(0))
            elif op == "rb":
                if len(b) > 1: b.append(b.pop(0))
            elif op == "rr":
                if len(a) > 1: a.append(a.pop(0))
                if len(b) > 1: b.append(b.pop(0))
            elif op == "rra":
                if len(a) > 1: a.insert(0, a.pop())
            elif op == "rrb":
                if len(b) > 1: b.insert(0, b.pop())
            elif op == "rrr":
                if len(a) > 1: a.insert(0, a.pop())
                if len(b) > 1: b.insert(0, b.pop())
            else:
                return False, f"Invalid Instruction: {op}"
        except IndexError:
             return False, f"Stack Underflow on {op}"

    if b: return False, "Stack B not empty"
    if a != sorted(a): return False, "Stack A not sorted"
    return True, "OK"

def run_test(num_count, ops_limit, iterations, log_errors=True):
    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[0;96m"
    RESET = "\033[0m"

    print(f"\n--- Running {iterations} tests with {num_count} numbers (Ops limit: {CYAN}<{ops_limit + 1}{RESET}) ---")

    failures = 0
    sort_failures = 0
    total_ops = 0
    max_ops_seen = 0

    if log_errors:
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(f"--- Error Log for {num_count} numbers ---\n")

    for i in range(1, iterations + 1):
        numbers = generate_random_numbers(num_count)
        args = [str(n) for n in numbers]

        try:
            process = subprocess.run([PUSH_SWAP_PATH] + args, capture_output=True, text=True)
            output = process.stdout.strip()
            if process.returncode != 0:
                print(f"\n{RED}CRASH on test {i}! (Return Code: {process.returncode}){RESET}")
                if log_errors:
                    with open(ERROR_LOG_FILE, "a") as f:
                        f.write(f"CRASH: Return code {process.returncode}. Args: {' '.join(args)}\n")
                return

            if not output: ops_count = 0
            else: ops_count = len(output.split('\n'))

            total_ops += ops_count
            max_ops_seen = max(max_ops_seen, ops_count)

            is_sorted, reason = internal_python_checker(numbers, output)

            if not is_sorted:
                sort_failures += 1
                print(f"\n{RED}SORT FAIL on test {i}: {reason}{RESET}")
                if log_errors:
                     with open(ERROR_LOG_FILE, "a") as f:
                        f.write(f"FAIL: {reason}. Args: {' '.join(args)}\n")

            if ops_count > ops_limit:
                failures += 1
                if log_errors:
                    with open(ERROR_LOG_FILE, "a") as f:
                        f.write(f"LIMIT EXCEEDED: {ops_count} moves. Args: {' '.join(args)}\n")

            print(f"\rTest {i}/{iterations} | Max: {max_ops_seen}", end="")
            sys.stdout.flush()

        except Exception as e:
            print(f"\nError running test {i}: {e}")
            return

    print()
    avg = total_ops / iterations if iterations > 0 else 0
    max_ops_color = GREEN if max_ops_seen <= ops_limit else RED
    avg_color = GREEN if avg < ops_limit else RED
    failures_color = GREEN if failures == 0 else RED
    sort_fail_color = GREEN if sort_failures == 0 else RED

    print(f"Sorting Status: {sort_fail_color}{'ALL SORTED' if sort_failures == 0 else f'{sort_failures} FAILED'}{RESET}")
    print(f"Max ops: {max_ops_color}{max_ops_seen}{RESET} ops")
    print(f"Average: {avg_color}{avg:.1f}{RESET} ops")
    print(f"Limit Breaches: {failures_color}{failures}{RESET}/{iterations}")

if __name__ == "__main__":
    try:
        subprocess.run([PUSH_SWAP_PATH], capture_output=True)
    except FileNotFoundError:
        print("Error: ./push_swap not found. Compile it first!")
        sys.exit(1)

    with open(ERROR_LOG_FILE, "w") as f: f.write("")

    # --- Small Tests ---
    run_test(num_count=2, ops_limit=1, iterations=10, log_errors=True)
    run_test(num_count=3, ops_limit=2, iterations=10, log_errors=True)
    run_test(num_count=4, ops_limit=12, iterations=10, log_errors=True)
    run_test(num_count=5, ops_limit=12, iterations=10, log_errors=True)

    # --- Medium Tests ---
    run_test(num_count=24, ops_limit=200, iterations=10, log_errors=True)
    run_test(num_count=42, ops_limit=400, iterations=10, log_errors=True)
    run_test(num_count=99, ops_limit=700, iterations=10, log_errors=True)

    # --- Large Tests ---
    run_test(num_count=142, ops_limit=1500, iterations=10, log_errors=True)
    run_test(num_count=240, ops_limit=2500, iterations=10, log_errors=True)
    run_test(num_count=330, ops_limit=3500, iterations=10, log_errors=True)
    run_test(num_count=469, ops_limit=5000, iterations=10, log_errors=True)
    run_test(num_count=500, ops_limit=5500, iterations=1000, log_errors=True)
