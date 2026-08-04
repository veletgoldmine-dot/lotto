"use client";

import { useSyncExternalStore } from "react";
import {
  clearHistory,
  getHistorySnapshot,
  getHistoryServerSnapshot,
  subscribeHistory,
} from "./history";
import { ballColor } from "./lotto";

function formatTime(ts: number): string {
  return new Date(ts).toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function LottoHistory() {
  const records = useSyncExternalStore(
    subscribeHistory,
    getHistorySnapshot,
    getHistoryServerSnapshot
  );

  // 최신순 정렬
  const sorted = [...records].sort((a, b) => b.drawnAt - a.drawnAt);

  return (
    <section className="w-full max-w-2xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
          내 로또 기록 📒
        </h2>
        {sorted.length > 0 && (
          <button
            type="button"
            onClick={clearHistory}
            className="rounded-full border border-gray-300 px-3 py-1 text-xs text-gray-500 transition hover:bg-gray-100 dark:border-zinc-700 dark:text-zinc-400 dark:hover:bg-zinc-800"
          >
            기록 지우기
          </button>
        )}
      </div>

      {sorted.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-gray-200 py-10 text-center text-sm text-gray-400 dark:border-zinc-800 dark:text-zinc-500">
          아직 뽑은 번호가 없어요. 위에서 번호를 뽑아보세요!
        </p>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-500 dark:border-zinc-800 dark:text-zinc-400">
                <th className="whitespace-nowrap px-4 py-3 font-medium">
                  생성한 시각
                </th>
                <th className="px-4 py-3 font-medium">생성된 번호</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((record) => (
                <tr
                  key={record.drawnAt}
                  className="border-b border-gray-100 last:border-0 dark:border-zinc-800/60"
                >
                  <td className="whitespace-nowrap px-4 py-3 align-middle text-gray-600 dark:text-zinc-300">
                    {formatTime(record.drawnAt)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap items-center gap-1.5">
                      {record.numbers.map((n, i) => (
                        <span
                          key={i}
                          className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${ballColor(
                            n
                          )}`}
                        >
                          {n}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
