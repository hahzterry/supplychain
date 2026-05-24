const LOGO_PATH = '/agi-logo.png';

let _cachedBase64: string | null = null;
let _cachedBlob: Blob | null = null;

export async function getLogoBase64(): Promise<string> {
  if (_cachedBase64) return _cachedBase64;
  const res = await fetch(LOGO_PATH);
  const blob = await res.blob();
  _cachedBlob = blob;
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      _cachedBase64 = (reader.result as string).split(',')[1];
      resolve(_cachedBase64);
    };
    reader.readAsDataURL(blob);
  });
}

export async function getLogoArrayBuffer(): Promise<ArrayBuffer> {
  if (_cachedBlob) return _cachedBlob.arrayBuffer();
  const res = await fetch(LOGO_PATH);
  _cachedBlob = await res.blob();
  return _cachedBlob.arrayBuffer();
}

export const LOGO_ASPECT_RATIO = 410 / 186; // width / height
