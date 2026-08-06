export const DEFAULT_CONTENT = {
    homepage_announcement: {
        enabled: true,
        title: "Registration Ongoing",
        body: "Parents are warmly invited to register early to secure a place at Little Oaks."
    },
    about: {
        intro: "At Little Oaks Montessori Kindergarten & Daycare, we provide a loving, safe and stimulating environment where children grow in knowledge, confidence, character and creativity. We serve families across Greater Mbarara while respecting every child's individuality and learning pace.",
        mission: "To give every child a loving, safe and stimulating start where knowledge, confidence, character and creativity grow together.",
        philosophy: "Little Oaks follows the Montessori philosophy. Children learn through hands-on, practical activities at their own pace, in prepared environments guided by caring teachers.",
        highlights: [
            "Montessori philosophy",
            "AI & digital learning programmes for children",
            "Hands-on learning",
            "Practical life skills",
            "Serving families across Greater Mbarara"
        ]
    },
    approach: {
        title: "Our Approach",
        body: "Children at Little Oaks are not judged, pressured or compared. Every child is unique and learns at their own pace. Learning is joyful, respectful and confidence-building."
    },
    programmes: {
        day_care: {
            title: "Day Care",
            ages: "6 months – 3 years",
            description: "A warm, safe and stimulating space where our youngest children play, learn and grow.",
            items: [
                "Early stimulation",
                "Play",
                "Daily routines",
                "Hygiene",
                "Social development",
                "Confidence building"
            ]
        },
        kindergarten: {
            title: "Kindergarten",
            ages: "3 – 6 years",
            description: "A rich Montessori learning environment for growing minds and curious hearts.",
            items: [
                "Literacy",
                "Numeracy",
                "Language",
                "Early science",
                "Montessori learning",
                "Problem solving"
            ]
        }
    },
    sports_skills: {
        sports: ["Football", "Basketball", "Netball", "Swimming"],
        brain_games: ["Chess", "Darts", "Puzzles", "Strategy Games"],
        life_skills: ["Cooking", "Housekeeping", "Gardening", "Health & Safety", "Environmental Care"],
        enrichment: ["Reading Club", "Arts & Crafts"]
    },
    admissions_notice: {
        enabled: true,
        title: "Registration Ongoing",
        body: "Parents are warmly invited to register early to secure a place at Little Oaks."
    },
    location: {
        place: "Nsikye, Nyamitanga",
        details: [
            "Along Kikagati–Isingiro Road",
            "700m after Holy Innocents Hospital",
            "Mbarara City"
        ],
        maps_url: "https://www.google.com/maps/search/?api=1&query=Nsikye+Nyamitanga+Mbarara"
    },
    contact: {
        phones: ["0705 074279", "0762 023393"],
        email: "info@littleoaks.ug",
        address: "Nsikye, Nyamitanga, Along Kikagati–Isingiro Road, 700m after Holy Innocents Hospital, Mbarara City",
        hours: "Mon–Fri, 7:00am – 5:00pm",
        whatsapp: "0705 074279"
    },
    gallery: {
        items: [
            { label: "Montessori classroom", url: "" },
            { label: "Outdoor play", url: "" },
            { label: "Art & craft", url: "" },
            { label: "Music & movement", url: "" },
            { label: "Gardening", url: "" },
            { label: "Sports day", url: "" },
            { label: "Story time", url: "" },
            { label: "Graduation", url: "" }
        ]
    }
};

function isPlainObject(value) {
    return value && typeof value === "object" && !Array.isArray(value);
}

function deepMerge(base, over) {
    if (!isPlainObject(base) || !isPlainObject(over)) {
        return over === undefined || over === null ? base : over;
    }
    const out = { ...base };
    for (const key of Object.keys(over)) {
        if (over[key] === undefined || over[key] === null) continue;
        out[key] = deepMerge(base[key], over[key]);
    }
    return out;
}

export function mergeSiteContent(savedSections) {
    return deepMerge(DEFAULT_CONTENT, savedSections || {});
}

let _cache = null;

export async function loadSiteContent() {
    if (_cache) return _cache;
    try {
        const response = await fetch("/api/site-content", {
            headers: { "Content-Type": "application/json" }
        });
        if (!response.ok) throw new Error(`site-content ${response.status}`);
        const data = await response.json();
        _cache = mergeSiteContent(data?.sections);
    } catch {
        _cache = DEFAULT_CONTENT;
    }
    return _cache;
}

export function getSiteContent() {
    return _cache || DEFAULT_CONTENT;
}

export async function refreshSiteContent() {
    _cache = null;
    return loadSiteContent();
}
