"use client";
import React, { useState, useEffect } from "react";

import { FaStar } from "react-icons/fa";

export default function EmployeesTable() {
    const [data, setData] = useState([]);
    const [filteredData, setFilteredData] = useState([]);

    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;

    const [search, setSearch] = useState("");

    useEffect(() => {
        const fetchData = async () => {
            const apiUrl = process.env.NEXT_PUBLIC_EMPINFO_API + '/api/employee/list';
            const response = await fetch(apiUrl, {
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + process.env.NEXT_PUBLIC_TOKEN,
                    "Content-Type": "application/json",
                }
            });
            const result = await response.json();
            setData(result.employees);
            setFilteredData(result.employees);
        };
        fetchData();
    }, []);

    useEffect(() => {
        const filtered = data.filter((item) =>
            item.empCode.toLowerCase().includes(search.toLowerCase())
        );
        setFilteredData(filtered);
        setCurrentPage(1);
    }, [search, data]);

    const totalPages = Math.ceil(filteredData.length / itemsPerPage);

    const currentData = filteredData.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

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

    return (
        <>
            <div className="flex space-x-4 mb-4">
                <input type="text" placeholder="Emp.code" onChange={(e) => setSearch(e.target.value)} value={search}
                       className="w-1/4 block rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-lime-600 sm:text-sm/6" />
            </div>
            <div className="relative overflow-x-auto">
                <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3">Emp.code</th>
                        <th scope="col" className="px-6 py-3">Position</th>
                        <th scope="col" className="px-6 py-3">Skill/Techstack</th>
                        <th scope="col" className="px-6 py-3">Additional Skills</th>
                        <th scope="col" className="px-6 py-3">Business Domains</th>
                        <th scope="col" className="px-6 py-3">Work Plan</th>
                    </tr>
                    </thead>
                    <tbody>
                    {currentData.map((item) => (
                        <tr key={item.id} className="bg-white border-b border-gray-200">
                            <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap align-top">{item.empCode}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.contractInfo ? (item.contractInfo.levelName + ' - ' + item.contractInfo.positionName) : '-/-'}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.skills.map((skill, skillIndex) => (
                                <div key={skillIndex} className="flex flex-col">
                                    <span className="flex items-center">{skill.proficiencyName} - {skill.skillName} {skill.isPrimary ? <FaStar className="text-lime-500 ml-1" /> : ''}</span>
                                </div>
                            ))}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">{item.additionalSkills.map((skill, skillIndex) => (
                                <div key={skillIndex} className="flex flex-col">
                                    <span className="flex items-center">{skill.proficiencyName} - {skill.additionalSkillName}</span>
                                </div>
                            ))}</td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top">
                                {item.businessDomains.map((domain, domainIndex) => (
                                    <div key={domainIndex} className="flex flex-col">
                                        <span className="flex items-center">{domain.businessDomainName}</span>
                                    </div>
                                ))}
                            </td>
                            <td className="px-6 py-4 font-normal text-gray-900 align-top"></td>
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