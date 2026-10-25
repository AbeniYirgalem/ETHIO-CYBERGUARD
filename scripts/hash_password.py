"""Generate a salted password hash.  Usage:  python -m scripts.hash_password"""

import getpass

from services.security.passwords import hash_password, validate_password_policy


def main() -> None:
    password = getpass.getpass("Password: ")
    problems = validate_password_policy(password)
    if problems:
        raise SystemExit("Rejected:\n- " + "\n- ".join(problems))
    print(hash_password(password))


if __name__ == "__main__":
    main()
