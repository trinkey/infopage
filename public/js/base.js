const dom = (id) => (document.getElementById(id));

function setCookie(name, value) {
  let date = new Date();
  date.setTime(date.getTime() + (356 * 24 * 60 * 60 * 1000));
  document.cookie = `${name}=${value};Path=/;Expires=${date.toUTCString()}`;
}

function eraseCookie(name) {
  document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function sha256(ascii) {
  function rightRotate(value, amount) {
    return (value >>> amount) | (value << (32 - amount));
  };

  let maxWord = Math.pow(2, 32);
  let i, j;
  let result = '';

  let words = [];
  let asciiBitLength = ascii["length"]*8;

  let hash = sha256.h = sha256.h || [];
  let k = sha256.k = sha256.k || [];
  let primeCounter = k["length"];

  let isComposite = {};
  for (let candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (i = 0; i < 313; i += candidate) {
        isComposite[i] = candidate;
      }
      hash[primeCounter] = (Math.pow(candidate, .5) * maxWord) | 0;
      k[primeCounter++] = (Math.pow(candidate, 1 / 3) * maxWord) | 0;
    }
  }

  ascii += '\x80'
  while (ascii["length"]%64 - 56) ascii += '\x00'
  for (i = 0; i < ascii["length"]; i++) {
    j = ascii.charCodeAt(i);
    if (j >> 8) return;
    words[i >> 2] |= j << ((3 - i) % 4) * 8;
  }
  words[words["length"]] = ((asciiBitLength / maxWord) | 0);
  words[words["length"]] = (asciiBitLength)

  for (j = 0; j < words["length"];) {
    let w = words.slice(j, j += 16);
    let oldHash = hash;
    hash = hash.slice(0, 8);

    let w15, a, temp1, temp2;

    for (i = 0; i < 64; i++) {
      w15 = w[i - 15], w2 = w[i - 2];
      a = hash[0], e = hash[4];
      temp1 = hash[7] + (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) + ((e & hash[5])^((~e) & hash[6])) + k[i] + (w[i] = (i < 16) ? w[i] : (w[i - 16] + (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3)) + w[i - 7] + (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))) | 0);
      temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22))  + ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
      hash = [(temp1 + temp2) | 0].concat(hash);
      hash[4] = (hash[4] + temp1) | 0;
    }

    for (i = 0; i < 8; i++) {
      hash[i] = (hash[i] + oldHash[i]) | 0;
    }
  }

  for (i = 0; i < 8; i++) {
    for (j = 3; j + 1; j--) {
      let b = (hash[i] >> (j * 8)) & 255;
      result += ((b < 16) ? 0 : '') + b.toString(16);
    }
  }
  return result;
};

function escapeHTML(text, forInput=false) {
  if (forInput) {
    return text.replaceAll("&", "&amp;")
               .replaceAll("<", "&lt;")
               .replaceAll("\"", "&quot;")
               .replaceAll("\n", " ");
  }
  return text.replaceAll("&", "&amp;")
             .replaceAll("<", "&lt;")
             .replaceAll("\"", "&quot;");
}

const icons = {
  1: '<svg style="fill: var(--text-low-opacity);" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M323.8 477.2c-38.2 10.9-78.1-11.2-89-49.4l-5.7-20c-3.7-13-10.4-25-19.5-35l-51.3-56.4c-8.9-9.8-8.2-25 1.6-33.9s25-8.2 33.9 1.6l51.3 56.4c14.1 15.5 24.4 34 30.1 54.1l5.7 20c3.6 12.7 16.9 20.1 29.7 16.5s20.1-16.9 16.5-29.7l-5.7-20c-5.7-19.9-14.7-38.7-26.6-55.5-5.2-7.3-5.8-16.9-1.7-24.9s12.3-13 21.3-13H448c8.8 0 16-7.2 16-16 0-6.8-4.3-12.7-10.4-15-7.4-2.8-13-9-14.9-16.7s.1-15.8 5.3-21.7c2.5-2.8 4-6.5 4-10.6 0-7.8-5.6-14.3-13-15.7-8.2-1.6-15.1-7.3-18-15.2s-1.6-16.7 3.6-23.3c2.1-2.7 3.4-6.1 3.4-9.9 0-6.7-4.2-12.6-10.2-14.9-11.5-4.5-17.7-16.9-14.4-28.8.4-1.3.6-2.8.6-4.3 0-8.8-7.2-16-16-16h-97.5c-12.6 0-25 3.7-35.5 10.7l-61.7 41.1c-11 7.4-25.9 4.4-33.3-6.7s-4.4-25.9 6.7-33.3l61.7-41.1c18.4-12.3 40-18.8 62.1-18.8H384c34.7 0 62.9 27.6 64 62 14.6 11.7 24 29.7 24 50 0 4.5-.5 8.8-1.3 13 15.4 11.7 25.3 30.2 25.3 51 0 6.5-1 12.8-2.8 18.7 11.6 11.8 18.8 27.8 18.8 45.5 0 35.3-28.6 64-64 64h-92.3c4.7 10.4 8.7 21.2 11.8 32.2l5.7 20c10.9 38.2-11.2 78.1-49.4 89zM32 384c-17.7 0-32-14.3-32-32V128c0-17.7 14.3-32 32-32h64c17.7 0 32 14.3 32 32v224c0 17.7-14.3 32-32 32H32z"/></svg>',
  2: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M100.5 176c-29 0-52.5 23.5-52.5 52.5V320c0 13.3-10.7 24-24 24S0 333.3 0 320v-91.5C0 173 45 128 100.5 128c29.6 0 57.6 13 76.7 35.6l130.2 153.8c10 11.8 24.6 18.6 40.1 18.6 29 0 52.5-23.5 52.5-52.5V192c0-13.3 10.7-24 24-24s24 10.7 24 24v91.5C448 339 403 384 347.5 384c-29.6 0-57.6-13-76.7-35.6L140.6 194.6c-10-11.8-24.6-18.6-40.1-18.6z"/></svg>',
  3: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="M323.8 34.8c-38.2-10.9-78.1 11.2-89 49.4l-5.7 20c-3.7 13-10.4 25-19.5 35l-51.3 56.4c-8.9 9.8-8.2 25 1.6 33.9s25 8.2 33.9-1.6l51.3-56.4c14.1-15.5 24.4-34 30.1-54.1l5.7-20c3.6-12.7 16.9-20.1 29.7-16.5s20.1 16.9 16.5 29.7l-5.7 20c-5.7 19.9-14.7 38.7-26.6 55.5-5.2 7.3-5.8 16.9-1.7 24.9s12.3 13 21.3 13H448c8.8 0 16 7.2 16 16 0 6.8-4.3 12.7-10.4 15-7.4 2.8-13 9-14.9 16.7s.1 15.8 5.3 21.7c2.5 2.8 4 6.5 4 10.6 0 7.8-5.6 14.3-13 15.7-8.2 1.6-15.1 7.3-18 15.2s-1.6 16.7 3.6 23.3c2.1 2.7 3.4 6.1 3.4 9.9 0 6.7-4.2 12.6-10.2 14.9-11.5 4.5-17.7 16.9-14.4 28.8.4 1.3.6 2.8.6 4.3 0 8.8-7.2 16-16 16h-97.5c-12.6 0-25-3.7-35.5-10.7l-61.7-41.1c-11-7.4-25.9-4.4-33.3 6.7s-4.4 25.9 6.7 33.3l61.7 41.1c18.4 12.3 40 18.8 62.1 18.8H384c34.7 0 62.9-27.6 64-62 14.6-11.7 24-29.7 24-50 0-4.5-.5-8.8-1.3-13 15.4-11.7 25.3-30.2 25.3-51 0-6.5-1-12.8-2.8-18.7 11.6-11.8 18.8-27.8 18.8-45.5 0-35.3-28.6-64-64-64h-92.3c4.7-10.4 8.7-21.2 11.8-32.2l5.7-20c10.9-38.2-11.2-78.1-49.4-89zM32 192c-17.7 0-32 14.3-32 32v224c0 17.7 14.3 32 32 32h64c17.7 0 32-14.3 32-32V224c0-17.7-14.3-32-32-32H32z"/></svg>',
  4: '<svg class="accent" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path d="m47.6 300.4 180.7 168.7c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9l180.7-168.7c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141-45.6-7.6-92 7.3-124.6 39.9l-12 12-1-12c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"/></svg>',
  add: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32V224H48c-17.7 0-32 14.3-32 32s14.3 32 32 32H192V432c0 17.7 14.3 32 32 32s32-14.3 32-32V288H400c17.7 0 32-14.3 32-32s-14.3-32-32-32H256V80z"/></svg>',
  x: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 342.6 150.6z"/></svg>',
  arrow: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path d="M438.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-160-160c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L338.8 224H32c-17.7 0-32 14.3-32 32s14.3 32 32 32h306.7L233.4 393.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l160-160z"/></svg>'
}
