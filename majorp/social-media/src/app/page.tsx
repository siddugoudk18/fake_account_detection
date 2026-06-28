import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import AppContent from "@/components/AppContent";

export default async function Home() {
  const cookieStore = await cookies();
  const userIdStr = cookieStore.get("userId")?.value;
  if (!userIdStr) redirect("/login");

  const userId = parseInt(userIdStr, 10);

  const currentUser = await prisma.user.findUnique({
    where: { id: userId },
  });

  if (!currentUser) redirect("/login");

  const posts = await prisma.post.findMany({
    orderBy: { createdAt: "desc" },
    include: {
      author: true,
      likes: true,
      comments: {
        include: { author: true },
        orderBy: { createdAt: "asc" },
      },
    },
  });

  const allUsers = await prisma.user.findMany({
    where: { id: { not: userId } },
    take: 10,
  });

  return (
    <AppContent currentUser={currentUser} posts={posts} allUsers={allUsers} />
  );
}
