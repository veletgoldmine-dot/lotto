export type LottoRecord = {
  drawnAt: number; // 생성한 시각 (epoch ms)
  birthDate: string;
  numbers: number[];
};

const STORAGE_KEY = "lotto-history";
export const HISTORY_UPDATED_EVENT = "lotto-history-updated";

export function loadHistory(): LottoRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(
      (r): r is LottoRecord =>
        typeof r?.drawnAt === "number" &&
        typeof r?.birthDate === "string" &&
        Array.isArray(r?.numbers)
    );
  } catch {
    return [];
  }
}

export function addHistory(record: LottoRecord): void {
  if (typeof window === "undefined") return;
  const next = [record, ...loadHistory()];
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    window.dispatchEvent(new Event(HISTORY_UPDATED_EVENT));
  } catch {
    // 저장 공간이 가득 찼거나 접근이 막힌 경우 조용히 무시
  }
}

export function clearHistory(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
    window.dispatchEvent(new Event(HISTORY_UPDATED_EVENT));
  } catch {
    // 무시
  }
}

// --- useSyncExternalStore용 스토어 (SSR 안전 + 안정적 스냅샷) ---

const EMPTY: LottoRecord[] = [];
let cachedRaw: string | null = null;
let cachedValue: LottoRecord[] = EMPTY;

export function subscribeHistory(callback: () => void): () => void {
  if (typeof window === "undefined") return () => {};
  // 같은 탭에서의 갱신 + 다른 탭에서의 localStorage 변경 모두 반영
  window.addEventListener(HISTORY_UPDATED_EVENT, callback);
  window.addEventListener("storage", callback);
  return () => {
    window.removeEventListener(HISTORY_UPDATED_EVENT, callback);
    window.removeEventListener("storage", callback);
  };
}

// 원본 문자열이 그대로면 같은 배열 참조를 돌려줘 리렌더 루프를 막는다.
export function getHistorySnapshot(): LottoRecord[] {
  if (typeof window === "undefined") return EMPTY;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (raw === cachedRaw) return cachedValue;
  cachedRaw = raw;
  cachedValue = loadHistory();
  return cachedValue;
}

export function getHistoryServerSnapshot(): LottoRecord[] {
  return EMPTY;
}
