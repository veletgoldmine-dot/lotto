"use client";

import { useState } from "react";
import LottoBall from "./LottoBall";
import { drawLottoNumbers } from "./lotto";
import { addHistory } from "./history";
import { playFanfare, unlockAudio } from "./sound";

const CURRENT_YEAR = new Date().getFullYear();

type Result = {
  birthDate: string;
  numbers: number[];
  drawId: number;
};

export default function LottoForm() {
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");
  const [day, setDay] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState<Result | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    unlockAudio();

    const y = Number(year);
    const m = Number(month);
    const d = Number(day);

    if (!year || !month || !day) {
      setError("년, 월, 일을 모두 입력해주세요.");
      return;
    }

    const date = new Date(y, m - 1, d);
    const isValid =
      date.getFullYear() === y &&
      date.getMonth() === m - 1 &&
      date.getDate() === d;

    if (!isValid || y < 1900 || y > CURRENT_YEAR) {
      setError("올바른 생년월일을 입력해주세요.");
      return;
    }

    setError("");
    const birthDate = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(
      2,
      "0"
    )}`;

    const numbers = drawLottoNumbers(birthDate);
    const drawId = Date.now();

    setResult({ birthDate, numbers, drawId });
    addHistory({ drawnAt: drawId, birthDate, numbers });
  };

  return (
    <div className="flex w-full max-w-md flex-col items-center gap-8">
      <form
        onSubmit={handleSubmit}
        className="flex w-full flex-col items-center gap-4"
      >
        <div className="flex w-full items-center gap-2">
          <input
            type="number"
            inputMode="numeric"
            placeholder="년(YYYY)"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="w-full min-w-0 rounded-full border border-purple-200 bg-white px-4 py-3 text-center text-gray-700 shadow-sm outline-none focus:border-purple-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
          <input
            type="number"
            inputMode="numeric"
            placeholder="월"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="w-full min-w-0 rounded-full border border-purple-200 bg-white px-4 py-3 text-center text-gray-700 shadow-sm outline-none focus:border-purple-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
          <input
            type="number"
            inputMode="numeric"
            placeholder="일"
            value={day}
            onChange={(e) => setDay(e.target.value)}
            className="w-full min-w-0 rounded-full border border-purple-200 bg-white px-4 py-3 text-center text-gray-700 shadow-sm outline-none focus:border-purple-400 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}

        <button
          type="submit"
          className="w-full rounded-full bg-gradient-to-r from-purple-600 to-pink-500 px-8 py-3 font-semibold text-white shadow-lg transition hover:scale-105 hover:shadow-xl active:scale-95"
        >
          번호 뽑기
        </button>
      </form>

      {result && (
        <div className="flex flex-col items-center gap-4">
          <p className="text-sm text-gray-500 dark:text-zinc-400">
            {result.birthDate} 생일의 행운의 로또 번호예요
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {result.numbers.map((n, i) => (
              <LottoBall
                key={`${result.drawId}-${i}`}
                finalNumber={n}
                delay={i * 700}
                index={i}
                onRevealed={
                  i === result.numbers.length - 1 ? playFanfare : undefined
                }
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
