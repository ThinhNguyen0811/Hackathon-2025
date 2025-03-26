import React from 'react';
import RequestDetail from "../../../components/RequestDetail";

export default async function RequestDetailPage({ params }) {
    const { id } = await params;

    return (
        <div>
            <RequestDetail id={id}/>
        </div>
    );
}