import type { Metadata } from "next";
import { Figtree, Newsreader } from "next/font/google";
import "./globals.css";
import { TopBar } from "@/components/chrome/TopBar";
import { Sidebar } from "@/components/chrome/Sidebar";
import { currentMember } from "@/lib/member";

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  axes: ["opsz"],
});

const figtree = Figtree({ variable: "--font-figtree", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "One Action · Lean In Connect",
  description: "The One Action, held by the platform between meetings.",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const member = await currentMember();
  return (
    <html
      lang="en"
      className={`${newsreader.variable} ${figtree.variable} h-full`}
    >
      <body className="min-h-full">
        <TopBar member={member} />
        <div className="flex">
          <Sidebar />
          <main className="min-w-0 flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
