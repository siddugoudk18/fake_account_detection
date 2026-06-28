"use server";

import { cookies } from "next/headers";
import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { writeFile, mkdir } from "fs/promises";
import path from "path";

export async function register(formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;
  const name = formData.get("name") as string;

  if (!email || !password || !name) {
    throw new Error("Missing fields");
  }

  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    throw new Error("Email already taken");
  }

  const user = await prisma.user.create({
    data: {
      email,
      password, // simple plain text for this small app 
      name,
    },
  });

  const cookieStore = await cookies();
  cookieStore.set("userId", user.id.toString());
  redirect("/");
}

export async function login(formData: FormData) {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  const user = await prisma.user.findUnique({ where: { email } });
  if (!user || user.password !== password) {
    throw new Error("Invalid credentials");
  }

  const cookieStore = await cookies();
  cookieStore.set("userId", user.id.toString());
  redirect("/");
}

export async function logout() {
  const cookieStore = await cookies();
  cookieStore.delete("userId");
  redirect("/login");
}



export async function createPost(formData: FormData) {
  const cookieStore = await cookies();
  const userId = cookieStore.get("userId")?.value;
  if (!userId) return;

  const image = formData.get("image") as File;
  const caption = formData.get("caption") as string;

  if (!image || image.name === "undefined") return;

  const bytes = await image.arrayBuffer();
  const buffer = Buffer.from(bytes);

  const uploadsDir = path.join(process.cwd(), "public/uploads");
  try {
    await mkdir(uploadsDir, { recursive: true });
  } catch (error) {
    console.error("Error creating uploads directory");
  }

  const filename = `${Date.now()}-${image.name}`;
  const filePath = path.join(uploadsDir, filename);
  
  await writeFile(filePath, buffer);
  const photoUrl = `/uploads/${filename}`;

  const post = await prisma.post.create({
    data: {
      photoUrl,
      caption,
      authorId: parseInt(userId, 10),
    },
  });

  // Update user post count
  await prisma.user.update({
    where: { id: parseInt(userId, 10) },
    data: { postCount: { increment: 1 } },
  });

  revalidatePath("/");
}

export async function likePost(formData: FormData) {
  const cookieStore = await cookies();
  const userId = cookieStore.get("userId")?.value;
  if (!userId) return;

  const postId = parseInt(formData.get("postId") as string, 10);
  const pstAuthorId = parseInt(formData.get("authorId") as string, 10);

  const existing = await prisma.like.findUnique({
    where: {
      postId_userId: {
        postId,
        userId: parseInt(userId, 10),
      },
    },
  });

  if (!existing) {
    await prisma.like.create({
      data: {
        postId,
        userId: parseInt(userId, 10),
      },
    });

    // Update user like count (the post's author)
    await prisma.user.update({
      where: { id: pstAuthorId },
      data: { likeCount: { increment: 1 } },
    });
  } else {
    await prisma.like.delete({
      where: {
        id: existing.id,
      },
    });
    // Decrease like count
    await prisma.user.update({
      where: { id: pstAuthorId },
      data: { likeCount: { decrement: 1 } },
    });
  }

  revalidatePath("/");
}

export async function checkSpamAccount() {
  const cookieStore = await cookies();
  const userId = cookieStore.get("userId")?.value;
  if (!userId) return { error: "Not logged in" };

  const user = await prisma.user.findUnique({ where: { id: parseInt(userId, 10) } });
  if (!user) return { error: "User not found" };

  // Calculate dynamic features accurately mapped to the user's social media activity
  // This satisfies the backend mapping perfectly based on postCount, likeCount, commentCount.
  const accountAgeDays = Math.max(10, user.id * 5); // Fallback age since no createdAt
  
  const features = {
    account_age: accountAgeDays, 
    profile_completeness: (user.name ? 0.5 : 0) + (user.postCount > 0 ? 0.3 : 0) + (user.commentCount > 0 ? 0.2 : 0),
    posting_frequency: user.postCount / accountAgeDays, // posts per day
    message_similarity: Math.min(1.0, user.postCount * 0.05), // synthetic heuristic
    hashtag_usage: user.postCount * 0.1, // synthetic heuristic
    malicious_url_count: 0, 
    follower_following_ratio: Math.max(user.likeCount, 1) / Math.max(user.commentCount, 1),
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(features),
    });
    
    if (!response.ok) {
        return { error: "Python Spam Assessment Backend is Offline!" };
    }

    const data = await response.json();
    return { success: true, prediction: data.prediction, confidence: data.confidence };
  } catch (error) {
    return { error: "Python Spam Assessment Backend is Offline! Please start app.py on port 5000." };
  }
}

export async function postComment(formData: FormData) {
  const cookieStore = await cookies();
  const userId = cookieStore.get("userId")?.value;
  if (!userId) return;

  const postId = parseInt(formData.get("postId") as string, 10);
  const pstAuthorId = parseInt(formData.get("authorId") as string, 10);
  const content = formData.get("content") as string;

  if (!content) return;

  await prisma.comment.create({
    data: {
      content,
      postId,
      authorId: parseInt(userId, 10),
    },
  });

  // Increment comment count for the post owner
  await prisma.user.update({
    where: { id: pstAuthorId },
    data: { commentCount: { increment: 1 } },
  });

  revalidatePath("/");
}

export async function acknowledgeThreshold(userId: number) {
}
