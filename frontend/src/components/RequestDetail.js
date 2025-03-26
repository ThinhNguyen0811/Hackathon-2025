"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { FaProjectDiagram, FaUser, FaCalendarAlt, FaBookmark, FaChevronLeft } from "react-icons/fa";

const RequestDetail = (params) => {
    const [request, setRequest] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [suggestLoading, setSuggestLoading] = useState(false);
    const [suggestError, setSuggestError] = useState(null);

    const [matchedResources, setMatchedResources] = useState([]);
    const [users, setUsers] = useState([]);

    const handleSuggestMe = async () => {
        setSuggestLoading(true);
        try {
            const apiUrl = `${process.env.NEXT_PUBLIC_AI_ENDPOINT}/api/match`;
            let description = request.requestNote;
            for(const r in request.resourceDetails) {
                const resource = request.resourceDetails[r]
                const additionSkills = resource.additionalSkills.map((skill) => {
                    return skill.skillName;
                })
                description += `\n Need ${resource.requestedQuantity} ${resource.primarySkillName}`
                if (additionSkills.length) {
                    description += ` with additional skills: ${additionSkills}`;
                }
                if (resource.requirementNote) {
                    description += ` and note: ${resource.requirementNote}`;
                }
            }

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "ngrok-skip-browser-warning": 1,
                },
                body: JSON.stringify({
                    description: "We need to develop a modern e-commerce platform for a fashion retailer. The website should be built using React JS for the frontend, with Node.js. We're looking for a senior developer who understands retail and e-commerce. The project starts on March 25, 2025.",
                }),
            });
            const result = await response.json();

            if (!Object.keys(result.recommended_employees).length) {
                setSuggestError(result.error)
            } else {
                setMatchedResources(result.recommended_employees);
            }

        } catch (error) {
            setSuggestError("Error fetching matched resources "+ error.toString())
        } finally {
            setSuggestLoading(false);
        }
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return new Intl.DateTimeFormat("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        }).format(date);
    };

    const toPercent = (value) => {
        return (value * 100).toFixed(2);
    }

    const nl2br = (str) => {
        return str.split("\n").map((line, index) => (
            <React.Fragment key={index}>
                {line}
                <br />
            </React.Fragment>
        ));
    }

    const getUserEmpCode = (id) => {
        for(const u in users) {
            const user = users[u];
            if (id == user.id) {
                return user.empCode;
            }
        }
        return null;
    }

    useEffect(() => {
        async function getRequestDetail() {
            try {
                const apiUrl = `${process.env.NEXT_PUBLIC_INSIDER_API}/apiv2/resource-requests/${params.id}`;
                const response = await fetch(apiUrl, {
                    method: "GET",
                    headers: {
                        "Authorization": "Bearer " + process.env.NEXT_PUBLIC_TOKEN,
                        "Content-Type": "application/json",
                    },
                });
                const result = await response.json();
                setRequest(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        async function getUsers() {
            try {
                const apiUrl = `${process.env.NEXT_PUBLIC_INSIDER_API}/api/user`;
                const response = await fetch(apiUrl, {
                    method: "GET",
                    headers: {
                        "Authorization": "Bearer " + process.env.NEXT_PUBLIC_TOKEN,
                        "Content-Type": "application/json",
                    },
                });
                const result = await response.json();
                setUsers(result.data);
            } catch (err) {
                console.log(err.message);
            }
        }
        getUsers();
        getRequestDetail();
    }, [params.id]);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <div className="">
            {/* Header */}
            <h1 className="text-2xl font-bold flex items-center">
                <Link href={`/`} className="flex items-center text-base font-normal mr-4 text-gray-500"><FaChevronLeft /></Link> Resource Request Detail | Request ID: {request.requestId}
            </h1>

            {/* Project Information */}
            <div className="mt-4 space-y-2 text-gray-700">
                <div className="flex items-center text-sm">
                    <div className="flex items-center w-3xs">
                        <span className="mr-2"><FaProjectDiagram /></span>
                        <span className="font-medium text-gray-900">Request Type:</span>
                    </div>
                    <span
                        className="inline-flex items-center rounded-md bg-yellow-50 px-2 py-1 text-xs font-medium text-yellow-800 ring-1 ring-yellow-600/20 ring-inset">Resource</span>
                </div>
                <div className="flex items-center text-sm">
                    <div className="flex items-center w-3xs">
                        <span className="mr-2"><FaBookmark /></span>
                        <span className="font-medium text-gray-900">Project Name:</span>
                    </div>
                    <span>{request.targetName}</span>
                </div>
                <div className="flex items-center text-sm">
                    <div className="flex items-center w-3xs">
                        <span className="mr-2"><FaUser /></span>
                        <span className="font-medium text-gray-900">Creator:</span>
                    </div>
                    <span>{request.creatorUserCode}</span>
                </div>
                <div className="flex items-center text-sm">
                    <div className="flex items-center w-3xs">
                        <span className="mr-2"><FaCalendarAlt /></span>
                        <span className="font-medium text-gray-900">Creation time:</span>
                    </div>
                    <span>{formatDate(request.creationTime)}</span>
                </div>
            </div>

            {/* Request Note */}
            <div className="mt-6">
                <h2 className="text-base font-bold text-gray-900">REQUEST NOTE</h2>
                <div className="list-decimal list-inside mt-2 text-gray-900 text-sm leading-normal">
                    {nl2br(request.requestNote)}
                </div>
            </div>

            {/* Request Details Table */}
            <div className="mt-6">
                <h2 className="text-base font-bold text-gray-900 mb-2">REQUEST DETAILS</h2>
                <div className="relative overflow-x-auto">
                    <table className="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
                        <thead
                            className="text-xs text-gray-700 uppercase bg-gray-50">
                        <tr>
                            <th scope="col" className="px-6 py-3">
                                ID
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Requested Quantity
                            </th>
                            <th scope="col" className="px-6 py-3">
                                In Demand
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Primary Skills
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Additional Skills
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Requirement Note
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Assignee
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Expected Quantity
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Note
                            </th>
                            <th scope="col" className="px-6 py-3">
                                Status
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        {request.resourceDetails.map((resource, index) => (
                            <tr key={index} className="bg-white border-b border-gray-200">
                                <th scope="row"
                                    className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap  align-top">
                                    {resource.id}
                                </th>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {resource.requestedQuantity}
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {resource.inDemand}
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {resource.primarySkillName}
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {
                                        resource.additionalSkills.map((skill, skillIndex) => (
                                            <div key={skillIndex}>
                                                {skill.skillName}
                                            </div>
                                        ))
                                    }
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    <div className="mb-1 min-h-10">
                                        <textarea value={resource.requirementNote} readOnly className="bg-gray-100 p-2 h-20" />
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {
                                        resource.resourceAssignments.map((assignee, assigneeIndex) => (
                                            <div key={assigneeIndex} className="mb-1 h-20">
                                                <input value={getUserEmpCode(assignee.assigneeId) || ''} readOnly={true} className="bg-gray-50 p-2"/>
                                            </div>
                                        ))
                                    }
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {
                                        resource.resourceAssignments.map((assignee, assigneeIndex) => (
                                            <div key={assigneeIndex} className="mb-1 h-20">
                                                <input value={assignee.expectedQuantity} readOnly={true} className="bg-gray-100 p-2 text-center"/>
                                            </div>
                                        ))
                                    }
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {
                                        resource.resourceAssignments.map((assignee, assigneeIndex) => (
                                            <div key={assigneeIndex} className="mb-1 min-h-10">
                                                <textarea value={assignee.note} className="bg-gray-100 p-2 h-20" readOnly />
                                            </div>
                                        ))
                                    }
                                </td>
                                <td className="px-6 py-4 text-gray-900 align-top">
                                    {
                                        resource.resourceAssignments.map((assignee, assigneeIndex) => (
                                            <div key={assigneeIndex} className="h-20">
                                                {assignee.status}
                                            </div>
                                        ))
                                    }
                                </td>
                            </tr>
                        ))}

                        </tbody>
                    </table>
                </div>
            </div>

            {/* Suggest Button */}
            <div className="mt-6 text-right">
                <button onClick={handleSuggestMe}
                        className="text-white bg-lime-600 hover:bg-lime-700 focus:ring-4 focus:outline-none focus:ring-lime-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center cursor-pointer">
                    Suggest me
                </button>
            </div>

            {suggestLoading && <div role="status" className="text-center">
                <svg aria-hidden="true"
                     className="inline w-8 h-8 text-gray-200 animate-spin fill-lime-500"
                     viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                        fill="currentColor"/>
                    <path
                        d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                        fill="currentFill"/>
                </svg>
                <span className="sr-only">Loading...</span>
            </div>}

            {suggestError && <div className="text-base text-center leading-normal">{suggestError}</div>}

            {/* Matched Resources Display */}
            {!suggestLoading && matchedResources.length > 0 && (
                <div className="mt-6">
                    <h3 className="text-base font-bold text-gray-900 mb-2">MATCHED RESOURCES:</h3>
                    <div className="employee-list grid grid-cols-2 gap-4">
                        {matchedResources.map((employee, index) => (
                            <div key={index} className="employee-card border-l-4 border-lime-600 bg-white rounded-md p-5 shadow-sm">
                                <div className="employee-header flex items-center justify-between mb-2">
                                    <h3 className="text-slate-900 uppercase text-base bold">{employee.employee}</h3>
                                    <div className="match-score text-sm"><span
                                        className="bg-lime-600 text-white px-1 rounded-xs">{toPercent(employee.overall_match_score)}%</span> Match
                                    </div>
                                </div>

                                <div className="employee-meta flex space-x-2">
                                    <div
                                        className="badge availability-badge text-sm bg-lime-100 text-lime-600 px-3 py-1 rounded-full">Skill Fit: {toPercent(employee.detailed_scoring_breakdown.skill_fit)}%</div>
                                    <div
                                        className="badge availability-badge text-sm bg-lime-100 text-lime-600 px-3 py-1 rounded-full">Domain: {toPercent(employee.detailed_scoring_breakdown.domain_expertise_alignment)}%</div>
                                    <div
                                        className="badge availability-badge text-sm bg-lime-100 text-lime-600 px-3 py-1 rounded-full">Exp: {toPercent(employee.detailed_scoring_breakdown.experience_level_appropriateness)}%</div>
                                </div>

                                <div className="match-progress bg-gray-200 my-3 h-2 rounded-sm">
                                    <div className="progress-bar bg-lime-600 h-full rounded-sm"
                                         style={{ width: `${toPercent(employee.overall_match_score)}%` }}></div>
                                </div>

                                <div className="details space-y-1">
                                    {
                                        employee.potential_concerns_or_limitations.map((potential, potentialIndex) => (
                                            <div key={potentialIndex} className="text-sm leading-normal">{potential}</div>
                                        ))
                                    }
                                </div>

                                <div className="skill-list flex flex-wrap space-x-2 mt-4">
                                    {employee.key_strengths_and_relevant_experience.map((skill, skillIndex) => (
                                            <div key={skillIndex}
                                                 className="skill-item text-sm bg-gray-200 text-gray-700 px-3 py-1 rounded-full">{skill}</div>
                                        ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RequestDetail;