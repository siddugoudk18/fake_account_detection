"use client";

import { useState, useEffect } from "react";
import { createPost, likePost, postComment, logout, checkSpamAccount } from "@/app/actions";

interface User {
  id: number;
  name: string | null;
  postCount: number;
  likeCount: number;
  commentCount: number;
}

interface Comment {
  id: number;
  content: string;
  author: { name: string | null };
}

interface Like {
  userId: number;
}

interface Post {
  id: number;
  photoUrl: string;
  caption: string | null;
  authorId: number;
  author: { name: string | null };
  createdAt: Date;
  comments: Comment[];
  likes: Like[];
}

export default function AppContent({
  currentUser,
  posts,
  allUsers,
}: {
  currentUser: User;
  posts: Post[];
  allUsers: User[];
}) {
  const [showThresholdPopup, setShowThresholdPopup] = useState(false);
  const [spamStatus, setSpamStatus] = useState<string | null>(null);
  const [spamLoading, setSpamLoading] = useState(false);

  const handleSpamCheck = async () => {
    setSpamLoading(true);
    setSpamStatus("Calculating Score...");
    try {
      const res = await checkSpamAccount();
      if (res?.error) {
        setSpamStatus(res.error);
      } else if (res?.success) {
        const confidenceText = res.confidence ? `Score: ${res.confidence}%` : "";
        setSpamStatus(res.prediction === "spam" ? `⚠️ Spam (${confidenceText})` : `✅ Legitimate (${confidenceText})`);
      } else {
        setSpamStatus("Failed to analyze");
      }
    } catch (e) {
      setSpamStatus("Error connecting to backend");
    }
    setSpamLoading(false);
  };

  useEffect(() => {
    handleSpamCheck();
  }, [currentUser.postCount, currentUser.commentCount, currentUser.likeCount]);

  useEffect(() => {
    // Show pop-up if post count reaches a predefined threshold, say 5.
    // Also, usually you'd track if it was already shown using localStorage.
    if (currentUser.postCount >= 5 && !localStorage.getItem("thresholdShown")) {
      setShowThresholdPopup(true);
      localStorage.setItem("thresholdShown", "true");
    }
  }, [currentUser.postCount]);

  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // function to fetch a specific user's spam status
  const [selectedUserSpamStatus, setSelectedUserSpamStatus] = useState<string | null>(null);
  const [selectedUserSpamLoading, setSelectedUserSpamLoading] = useState(false);

  const fetchSelectedUserSpam = async (userId: number) => {
    setSelectedUserSpamLoading(true);
    setSelectedUserSpamStatus("Calculating...");
    try {
      // We can use the same server action but we need to modify it or create a new one
      // Wait, checkSpamAccount() relies on cookies().get("userId"). We should make a new action 
      // checkSpamForUser(id) if needed. But for now we can just show their basic stats
    } catch (e) {
    }
    setSelectedUserSpamLoading(false);
  };

  const handleUserClick = (u: User) => {
    setSelectedUser(u);
  };

  return (
    <>
      <header className="app-header">
        <div className="app-brand">Vibe</div>
        <button
          onClick={() => logout()}
          style={{ fontWeight: "600", color: "var(--danger-color)" }}
        >
          Logout
        </button>
      </header>

      <main className="main-content">
        <div className="post-list">
          <div className="create-post-card">
            <h3 style={{ marginBottom: "1rem" }}>Create New Post</h3>
            <form action={createPost} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <input
                type="file"
                name="image"
                accept="image/*"
                className="input-field"
                required
              />
              <textarea
                name="caption"
                placeholder="What's on your mind?"
                className="input-field"
                rows={3}
                style={{ resize: "none" }}
              />
              <button type="submit" className="primary-btn">
                Post
              </button>
            </form>
          </div>

          {posts.map((post) => (
            <div key={post.id} className="post-card">
              <div className="post-header">
                <div className="avatar">{post.author.name?.charAt(0).toUpperCase()}</div>
                <div>
                  <div className="author-name">{post.author.name}</div>
                  <div className="post-time">{new Date(post.createdAt).toISOString()}</div>
                </div>
              </div>
              <img src={post.photoUrl} alt="Post image" className="post-image" />
              
              <div className="post-actions">
                <form action={likePost}>
                  <input type="hidden" name="postId" value={post.id} />
                  <input type="hidden" name="authorId" value={post.authorId} />
                  <button
                    type="submit"
                    className={`action-btn ${
                      post.likes.some((l) => l.userId === currentUser.id) ? "liked" : ""
                    }`}
                  >
                    <span>{post.likes.some((l) => l.userId === currentUser.id) ? "❤️" : "🤍"}</span>
                    <span>{post.likes.length} Likes</span>
                  </button>
                </form>
                <div className="action-btn">
                  <span>💬</span>
                  <span>{post.comments.length} Comments</span>
                </div>
              </div>

              {post.caption && <div className="post-caption">{post.caption}</div>}

              <div className="comments-section">
                {post.comments.map((comment) => (
                  <div key={comment.id} className="comment">
                    <span className="comment-author">{comment.author.name}</span>
                    <span>{comment.content}</span>
                  </div>
                ))}

                <form action={postComment} className="add-comment">
                  <input type="hidden" name="postId" value={post.id} />
                  <input type="hidden" name="authorId" value={post.authorId} />
                  <input
                    type="text"
                    name="content"
                    placeholder="Add a comment..."
                    className="comment-input"
                    required
                  />
                  <button type="submit" className="comment-btn">
                    Post
                  </button>
                </form>
              </div>
            </div>
          ))}
        </div>

        <aside className="sidebar">
          <div className="profile-card">
            <div className="profile-avatar">
              {currentUser.name?.charAt(0).toUpperCase()}
            </div>
            <h2 style={{ fontSize: "1.25rem", fontWeight: "700" }}>{currentUser.name}</h2>
            
            <div style={{ marginTop: "1rem" }}>
              <div
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "0.5rem",
                  background: spamStatus?.includes("Spam") ? "var(--danger-color)" : "var(--accent-color)",
                  border: "1px solid var(--border-color)",
                  color: "white",
                  fontSize: "0.85rem",
                  fontWeight: "600",
                  textAlign: "center",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "0.5rem"
                }}
              >
                {spamStatus || "Calculating Trust Score..."}
              </div>
            </div>

            <div className="profile-stats">
              <div className="stat">
                <span className="stat-val">{currentUser.postCount}</span>
                <span className="stat-label">Posts</span>
              </div>
              <div className="stat">
                <span className="stat-val">{currentUser.likeCount}</span>
                <span className="stat-label">Likes</span>
              </div>
              <div className="stat">
                <span className="stat-val">{currentUser.commentCount}</span>
                <span className="stat-label">Comments</span>
              </div>
            </div>
          </div>

          <div className="users-list">
            <h3>Explore Users</h3>
            {allUsers.length === 0 ? (
              <p style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>No other users yet.</p>
            ) : (
              allUsers.map((u) => (
                <div 
                  key={u.id} 
                  className="user-row" 
                  onClick={() => handleUserClick(u)}
                  style={{ 
                    cursor: "pointer", 
                    padding: "0.5rem", 
                    borderRadius: "0.5rem",
                    transition: "background 0.2s"
                  }}
                  onMouseOver={(e) => e.currentTarget.style.background = "rgba(255,255,255,0.05)"}
                  onMouseOut={(e) => e.currentTarget.style.background = "transparent"}
                >
                  <div
                    className="avatar"
                    style={{ width: "2rem", height: "2rem", fontSize: "0.8rem" }}
                  >
                    {u.name?.charAt(0).toUpperCase()}
                  </div>
                  <div style={{ fontSize: "0.9rem", fontWeight: "500" }}>{u.name}</div>
                </div>
              ))
            )}
          </div>
        </aside>
      </main>

      {selectedUser && (
        <div className="modal-overlay" onClick={() => setSelectedUser(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ minWidth: "300px" }}>
            <div className="profile-avatar" style={{ margin: "0 auto 1rem" }}>
              {selectedUser.name?.charAt(0).toUpperCase()}
            </div>
            <h2 style={{ marginBottom: "0.5rem" }}>{selectedUser.name}</h2>
            <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
              User ID: {selectedUser.id}
            </p>
            
            <div className="profile-stats" style={{ marginTop: "0", paddingTop: "0", borderTop: "none", marginBottom: "1.5rem" }}>
              <div className="stat">
                <span className="stat-val">{selectedUser.postCount}</span>
                <span className="stat-label">Posts</span>
              </div>
              <div className="stat">
                <span className="stat-val">{selectedUser.likeCount}</span>
                <span className="stat-label">Likes</span>
              </div>
              <div className="stat">
                <span className="stat-val">{selectedUser.commentCount}</span>
                <span className="stat-label">Comments</span>
              </div>
            </div>
            
            <button
              className="primary-btn"
              style={{ width: "100%" }}
              onClick={() => setSelectedUser(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {showThresholdPopup && (
        <div className="modal-overlay" onClick={() => setShowThresholdPopup(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">🎉</div>
            <h2 style={{ marginBottom: "1rem", color: "var(--primary-color)" }}>
              Congratulations!
            </h2>
            <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem" }}>
              You've just reached {currentUser.postCount} posts on Vibe. Keep sharing your moments!
            </p>
            <button
              className="primary-btn"
              style={{ width: "100%" }}
              onClick={() => setShowThresholdPopup(false)}
            >
              Continue
            </button>
          </div>

        </div>
      )}
    </>
  );
}
