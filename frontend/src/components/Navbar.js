import Link from "next/link";

export default function Navbar() {
    return (
        <nav className="mb-6 flex justify-between items-center bg-lime-600 text-white p-4 rounded-lg">
            <div className="text-lg font-bold">Smart Resource Allocation</div>
            <ul className="flex space-x-6">
                <li><Link href="/" className="hover:underline">Home</Link></li>
                <li><Link href="/employees" className="hover:underline">Employees</Link></li>
                <li><Link href="/settings" className="hover:underline">Settings</Link></li>
            </ul>
        </nav>
    );
}