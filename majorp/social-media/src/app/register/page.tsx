import { register } from "@/app/actions";
import Link from "next/link";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";

export default async function RegisterPage() {
  const cookieStore = await cookies();
  const userId = cookieStore.get("userId")?.value;
  if (userId) redirect("/");

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <form action={register} className="auth-form">
          <input
            name="name"
            type="text"
            placeholder="Full Name"
            className="input-field"
            required
          />
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
            Register
          </button>
        </form>
        <div style={{ marginTop: "1.5rem", textAlign: "center", color: "var(--text-muted)" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--primary-color)", fontWeight: "600" }}>
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}
