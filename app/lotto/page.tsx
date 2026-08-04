import Link from "next/link";
import LottoForm from "./LottoForm";
import LottoHistory from "./LottoHistory";

export default function LottoPage() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-10 bg-gradient-to-b from-indigo-50 via-white to-pink-50 px-6 py-16 dark:from-zinc-950 dark:via-black dark:to-zinc-950">
      <div className="text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">
          행운의 로또 🍀
        </h1>
        <p className="mt-3 text-gray-500 dark:text-zinc-400">
          생년월일을 입력하면 그 날의 행운의 로또 번호를 뽑아드려요.
        </p>
      </div>
      <LottoForm />
      <LottoHistory />
      <Link
        href="/"
        className="text-sm text-purple-600 underline-offset-4 hover:underline dark:text-purple-400"
      >
        오늘의 운세 보러가기
      </Link>
    </div>
  );
}
