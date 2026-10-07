export const MATH_FUNCS = {
  sum: (...args) => args.flat().reduce((a, b) => a + Number(b), 0),
  sub: (...args) => {
    const arr = args.flat().map(Number);
    return arr.reduce((a, b) => a - b);
  },
  min: (...args) => Math.min(...args.flat().map(Number)),
  max: (...args) => Math.max(...args.flat().map(Number)),
  avg: (...args) => {
    const arr = args.flat().map(Number);
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  },
  count: (...args) => args.flat().length,
  abs: Math.abs,
  floor: Math.floor,
  ceil: Math.ceil,
  round: Math.round,
  sqrt: Math.sqrt,
  pow: Math.pow,
};

export const FUNC_NAMES = Object.keys(MATH_FUNCS);
export const FUNC_VALUES = Object.values(MATH_FUNCS);