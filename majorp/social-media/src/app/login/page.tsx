import { login } from "@/app/actions";
import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

export default async function LoginPage() {
  const cookieStore = await cookies();
  const userId = cookieStore.get("userId")?.value;
  if (userId) redirect("/");

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Welcome Back</h1>
        <form action={login} className="auth-form">
          <input
            name="email"
            type="email"
            placeholder="Email Address"
            className="input-field"
            required
          />
          <input
            name="password"
            type="password"
            placeholder="Password"
            className="input-field"
            required
          />
          <button type="submit" className="primary-btn">
            Login
          </button>
        </form>
        <div style={{ marginTop: "1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
          Don't have an account?{" "}
          <Link href="/register" style={{ color: "var(--primary-color)", fontWeight: "600" }}>
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}
