import React from "react";

const settings = {
    skillTechstack: 0.2,
    domain: 0.1,
    experience: 0.15,
    workplan: 0.35,
    performance: 0.05,
    sdc: 0.15,
};

export default function SettingsForm() {
    return (
        <div className="space-y-4 max-w-sm">
            <h2 className="font-semibold">Criteria Rate Setting</h2>
            {Object.entries(settings).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                    <label className="block text-sm/6 font-medium text-gray-900">{key.replace(/([A-Z])/g, " $1")}</label>
                    <input type="number" value={value} className="block w-20 rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-lime-600 sm:text-sm/6" />
                </div>
            ))}
            <h2 className="font-semibold">Confidence score Setting</h2>
            <div className="flex justify-between">
                <input type="text" value={"50%"} className="block w-20 rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-lime-600 sm:text-sm/6" />
            </div>
        </div>
    );
}