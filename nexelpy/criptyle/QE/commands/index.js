import * as dom from './dom.js';
import * as classFx from './class.js';
import * as attrFx from './attr.js';
import * as styleFx from './style.js';
import * as utilFx from './util.js';
import { animate } from './animate.js';
import { copyClipboard, pasteClipboard } from './clipboard.js';
import { ajax } from './ajax.js';
import { runFunc } from '../core/run-func.js';
import { showModal, hideModal } from './modal.js';
import { popOver, popHide } from './popover.js';
import { transitionsMap } from '../transitions/index.js';
import * as timerFx from './timer.js';


  


export const commandsMap = {
  ...dom,
  ...classFx,
  ...attrFx,
  ...styleFx,
  ...utilFx,
  ...transitionsMap,
  ...timerFx,
  animate,
  copyClipboard,
  pasteClipboard,
  ajax,
  runFunc,
  showModal,
  hideModal,
  popOver,
  popHide
};