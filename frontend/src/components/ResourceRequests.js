"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";

export default function ResourceRequests() {
    const [data, setData] = useState([]);
    const [totalRecords, setTotalRecords] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const take = 10;

    const [search, setSearch] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            const apiUrl = process.env.NEXT_PUBLIC_INSIDER_API + '/apiv2/resource-requests/assignments/filter';
            const skip = (currentPage - 1) * take;
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Authorization": "Bearer " + process.env.NEXT_PUBLIC_TOKEN,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    assigneeIds: [],
                    completionStatus: {
                        from: 0,
                        to: 100,
                    },
                    creatorIds: [],
                    departments: [],
                    isDescending: true,
                    primarySkills: [],
                    requestDate: {
                        from: null,
                        to: null,
                    },
                    requestTypes: [],
                    skip: skip,
                    take: take,
                    sortBy: "RequestDate",
                    terms: search,
                }),
            });
            const result = await response.json();
            setData(result.result);
            setTotalRecords(result.total);
        };
        fetchData();
    }, [currentPage, search]);

    const totalPages = Math.ceil(totalRecords / take);

    const generatePagination = () => {
        const pages = [];
        if (totalPages <= 7) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            if (currentPage <= 4) {
                pages.push(1, 2, 3, 4, 5, "...", totalPages);
            } else if (currentPage >= totalPages - 3) {
                pages.push(1, "...", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
            } else {
                pages.push(1, "...", currentPage - 1, currentPage, currentPage + 1, "...", totalPages);
            }
        }
        return pages;
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return new Intl.DateTimeFormat("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric",
        }).format(date);
    };

    return (
        <>
            <h1 className="text-2xl font-bold flex items-center mb-4">
                Resource Requests
            </h1>
            <div className="flex space-x-4 mb-4">
                <input type="text" placeholder="Request ID" onChange={(e) => setSearch(e.target.value)} value={search}
                       className="w-1/4 block rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-lime-600 sm:text-sm/6" />
            </div>
            <div className="relative overflow-x-auto">
                <table className="w-full text-sm text-left rtl:text-right text-gray-500">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3">Request ID</th>
                        <th scope="col" className="px-6 py-3">Creator</th>
                        <th scope="col" className="px-6 py-3">Status</th>
                        <th scope="col" className="px-6 py-3">Request Type</th>
                        <th scope="col" className="px-6 py-3">Request Date</th>
                        <th scope="col" className="px-6 py-3">Requested Quantity</th>
                        <th scope="col" className="px-6 py-3">Primary Skill</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data.map((item, itemIndex) => (
                        <tr key={itemIndex} className="bg-white border-b border-gray-200">
                            <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap align-top">

                                <Link href={`/requests/${item.resourceRequestId}`} className="hover:underline">{item.requestId}</Link>
                            </td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.creatorUserCode}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">
                                <span
                                    className={`${item.status == 'Waiting' 
                                        ? 'bg-yellow-100 text-yellow-800' 
                                        : (item.status == 'In Progress' 
                                            ? 'bg-blue-100 text-blue-800' 
                                            : (item.status == 'Cancelled' ? 'bg-gray-100 text-gray-800 border border-gray-500' : '')
                                        )} whitespace-nowrap text-xs font-medium me-2 px-2.5 py-0.5 rounded-sm`}>{item.status}</span>
                            </td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.requestType}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{formatDate(item.requestDate)}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.requestedQuantity}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.primarySkillName}</td>
                        </tr>
                    ))}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="7" className={"px-6 py-4 text-right"}>
                                <nav aria-label="Page navigation example">
                                    <ul className="inline-flex -space-x-px text-sm">
                                        <li>
                                            <a href="#"
                                               onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                                               disabled={currentPage === 1}
                                               className="flex items-center justify-center px-3 h-8 ms-0 leading-tight text-gray-500 bg-white border border-e-0 border-gray-300 rounded-s-lg hover:bg-gray-100 hover:text-gray-700">Previous</a>
                                        </li>
                                        {generatePagination().map((page, index) =>
                                            page === "..." ? (
                                                <span key={index} className="px-3 py-2">...</span>
                                            ) : (
                                                <li key={index}>
                                                    <a href="#"
                                                       key={index}
                                                       onClick={() => setCurrentPage(page)}
                                                       className={`flex items-center justify-center px-3 h-8 leading-tight border border-gray-300 ${currentPage === page ? "bg-lime-600 text-white" : "bg-white text-gray-500 hover:bg-gray-100 hover:text-gray-700"}`}>{page}</a>
                                                </li>
                                            )
                                        )}

                                        <li>
                                            <a href="#"
                                               onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                                               disabled={currentPage === totalPages}
                                               className="flex items-center justify-center px-3 h-8 leading-tight text-gray-500 bg-white border border-gray-300 rounded-e-lg hover:bg-gray-100 hover:text-gray-700">Next</a>
                                        </li>
                                    </ul>
                                </nav>
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </>
    );
}