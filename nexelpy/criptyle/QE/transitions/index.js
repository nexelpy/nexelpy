import { slideDown, slideUp, slideToggle } from './slide.js';


export const transitionsMap = {
  slideDown,
  slideUp,
  slideToggle,
};

export async function runTransition(el, transition, delay, doChange) {
  const [type, ...args] = transition;
  const fn = transitionsMap[type];

  if (!fn) {
    console.error(`Transition "${type}" not found`);
    doChange();
    return;
  }

  if (delay > 0) {
    await new Promise(r => setTimeout(r, delay));
  }

  return fn(el, args, doChange);
}