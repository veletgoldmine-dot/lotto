"use client";

import { useEffect, useRef, useState } from "react";
import { ballColor } from "./lotto";
import { playReveal, playTick } from "./sound";

export default function LottoBall({
  finalNumber,
  delay,
  index,
  onRevealed,
}: {
  finalNumber: number;
  delay: number;
  index: number;
  onRevealed?: () => void;
}) {
  const [display, setDisplay] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);
  const onRevealedRef = useRef(onRevealed);

  useEffect(() => {
    onRevealedRef.current = onRevealed;
  });

  useEffect(() => {
    let rollInterval: ReturnType<typeof setInterval> | undefined;
    let stopTimeout: ReturnType<typeof setTimeout> | undefined;

    const startTimeout = setTimeout(() => {
      rollInterval = setInterval(() => {
        setDisplay(Math.floor(Math.random() * 45) + 1);
        playTick();
      }, 60);

      stopTimeout = setTimeout(() => {
        clearInterval(rollInterval);
        setDisplay(finalNumber);
        setRevealed(true);
        playReveal(index);
        onRevealedRef.current?.();
      }, 900);
    }, delay);

    return () => {
      clearTimeout(startTimeout);
      clearInterval(rollInterval);
      clearTimeout(stopTimeout);
    };
  }, [finalNumber, delay, index]);

  if (display === null) {
    return (
      <span className="flex h-14 w-14 animate-pulse items-center justify-center rounded-full bg-gray-200 shadow-inner dark:bg-zinc-700" />
    );
  }

  return (
    <span
      className={`flex h-14 w-14 items-center justify-center rounded-full text-lg font-bold shadow-md ${ballColor(
        display
      )} ${revealed ? "ball-pop" : ""}`}
    >
      {display}
    </span>
  );
}
