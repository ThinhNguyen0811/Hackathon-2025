'use client';
import React from 'react';
import RequestDetail from "../../../components/RequestDetail";

export default function RequestDetailPage({ params }) {
    const { id } = params;

    return (
        <div>
            <RequestDetail id={id}/>
        </div>
    );
}