/** True when an IPv4 address falls inside a CIDR block. Malformed input is simply "no". */
export function ipInCidr(ip: string, cidr: string): boolean {
  const toInt = (value: string): number | null => {
    const parts = value.trim().split('.');
    if (parts.length !== 4) return null;
    let out = 0;
    for (const part of parts) {
      if (!/^\d{1,3}$/.test(part)) return null;
      const n = Number(part);
      if (n > 255) return null;
      out = out * 256 + n;
    }
    return out;
  };
  const [base, bitsText] = cidr.split('/');
  const bits = Number(bitsText);
  const a = toInt(ip);
  const b = toInt(base ?? '');
  if (a === null || b === null || !Number.isInteger(bits) || bits < 0 || bits > 32) return false;
  const size = 2 ** (32 - bits);
  return Math.floor(a / size) === Math.floor(b / size);
}
