import Link from "next/link";

export default function Home() {
    return (
        <div className="bg-white p-6 shadow-md rounded-lg">
            <h1 className="text-2xl font-bold mb-4">Home Page</h1>
            <nav className="space-x-4">
                <Link href="/employees" className="text-blue-500 hover:underline">Employees</Link>
                <Link href="/settings" className="text-blue-500 hover:underline">Settings</Link>
                <Link href="/request-detail" className="text-blue-500 hover:underline">Request Detail</Link>
            </nav>
        </div>
    );
}