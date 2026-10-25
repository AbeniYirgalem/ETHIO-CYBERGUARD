/**
 * ETHIO-CYBERGUARD Comprehensive Localization Dictionary
 * High-accuracy cybersecurity terminology in English and Amharic (አማርኛ).
 * Incorporates authentic INSA, Ethio-CERT, and Ethiopian financial sector conventions.
 */

export type Language = 'en' | 'am';

export interface TranslationDictionary {
  // Navigation & Shell
  nav: {
    overview: string;
    pipeline: string;
    monitoring: string;
    incidents: string;
    threat_intel: string;
    investigation: string;
    phishing: string;
    typosquat: string;
    osint: string;
    awareness: string;
    assistant: string;
    risk: string;
    response: string;
    reports: string;
    settings: string;
    admin: string;
  };
  badges: {
    commonGraph: string;
    live: string;
    nlpForensics: string;
    openSquat: string;
    spiderFoot: string;
    simulations: string;
    sevenAgents: string;
    export: string;
  };
  // Header
  header: {
    title: string;
    defcon: string;
    subtitle: string;
    tickerPrefix: string;
    insaLink: string;
    rootSoc: string;
    searchPlaceholder: string;
    hudShortcut: string;
    apiLive: string;
    apiSimulated: string;
    apiChecking: string;
    ingestRate: string;
    muteSound: string;
    enableSound: string;
    languageToggle: string;
    notifications: string;
  };
  // Ticker alerts
  ticker: {
    cbe: string;
    ethioCert: string;
    openSquat: string;
    telecom: string;
    insa: string;
  };
  // Banner & Tenant Switcher
  banner: {
    activeTenant: string;
    role: string;
    dataMode: string;
    dataLive: string;
    dataSimulated: string;
    signOut: string;
    signIn: string;
    switchPublic: string;
    switchSoc: string;
    systemConnected: string;
    systemConnectedDesc: string;
    demoMode: string;
    demoModeDesc: string;
    dismiss: string;
  };
  // Scenario Simulator
  scenarios: {
    title: string;
    subtitle: string;
    ransomware: string;
    phishing: string;
    ddos: string;
    insider: string;
    injecting: string;
  };
  // Overview & Metrics
  overview: {
    title: string;
    totalIncidents: string;
    criticalIncidents: string;
    pendingActions: string;
    mttd: string;
    mttr: string;
    activeThreats: string;
    radarTitle: string;
    radarSubtitle: string;
    liveFeedTitle: string;
    liveFeedSubtitle: string;
    allSectors: string;
    financial: string;
    telecom: string;
    energy: string;
    government: string;
  };
  // Common terms & Actions
  common: {
    severity: string;
    status: string;
    critical: string;
    high: string;
    medium: string;
    low: string;
    info: string;
    active: string;
    investigating: string;
    contained: string;
    resolved: string;
    closed: string;
    pending: string;
    approved: string;
    rejected: string;
    executed: string;
    details: string;
    actions: string;
    filter: string;
    all: string;
    search: string;
    refresh: string;
    close: string;
    save: string;
    cancel: string;
    timestamp: string;
    target: string;
    source: string;
  };
  // Response & SOAR
  response: {
    title: string;
    subtitle: string;
    dualCustodyBanner: string;
    dualCustodyDesc: string;
    pendingApprovals: string;
    executedActions: string;
    approveBtn: string;
    rejectBtn: string;
    executeBtn: string;
    rollbackBtn: string;
    requester: string;
    approver: string;
    actionType: string;
  };
  // Phishing & Forensics
  phishing: {
    title: string;
    subtitle: string;
    analyzeBtn: string;
    samplePlaceholder: string;
    spfValid: string;
    dkimValid: string;
    dmarcValid: string;
    amharicKeywordsFound: string;
    telebirrShield: string;
    riskScore: string;
  };
  // Public Landing Page
  publicPage: {
    navHome: string;
    navAbout: string;
    navDocs: string;
    navContact: string;
    heroBadge: string;
    heroTitle: string;
    heroTitleHighlight: string;
    heroSubtitle: string;
    ctaEnterSoc: string;
    ctaLearnMore: string;
    feature1Title: string;
    feature1Desc: string;
    feature2Title: string;
    feature2Desc: string;
    feature3Title: string;
    feature3Desc: string;
    statsEps: string;
    statsEpsLabel: string;
    statsAgents: string;
    statsAgentsLabel: string;
    statsPass: string;
    statsPassLabel: string;
    footerText: string;
  };
}

export const TRANSLATIONS: Record<Language, TranslationDictionary> = {
  en: {
    nav: {
      overview: 'Overview',
      pipeline: 'Unified Pipeline',
      monitoring: 'Monitoring',
      incidents: 'Incidents',
      threat_intel: 'Threat Intel',
      investigation: 'Investigation',
      phishing: 'Phishing Analyzer',
      typosquat: 'Brand & Typosquat',
      osint: 'Attack Surface OSINT',
      awareness: 'Security Awareness',
      assistant: 'AI Security Assistant',
      risk: 'Risk & Analytics',
      response: 'Response Center',
      reports: 'Reports & Compliance',
      settings: 'Identity & RBAC',
      admin: 'Administration',
    },
    badges: {
      commonGraph: 'Common Graph',
      live: 'Live',
      nlpForensics: 'NLP / Forensics',
      openSquat: 'openSquat',
      spiderFoot: 'SpiderFoot',
      simulations: 'Simulations',
      sevenAgents: '7 Agents',
      export: 'Export',
    },
    header: {
      title: 'ETHIO-CYBERGUARD',
      defcon: 'DEFCON 2',
      subtitle: 'National AI SIEM & Incident Command • Critical Infrastructure',
      tickerPrefix: 'ETHIO-CERT LIVE WIRE:',
      insaLink: 'INSA LINK: SYNCHRONIZED',
      rootSoc: 'ADDIS ABABA ROOT SOC',
      searchPlaceholder: 'Press ⌘K or click to search indicators, assets, actions...',
      hudShortcut: '⌘K HUD',
      apiLive: 'LIVE REST',
      apiSimulated: 'SIMULATED DEMO',
      apiChecking: 'CHECKING',
      ingestRate: 'INGEST:',
      muteSound: 'Mute Tactical Audio Synthesizer',
      enableSound: 'Enable Tactical Audio Synthesizer',
      languageToggle: 'Toggle English / Amharic',
      notifications: 'Open Notifications',
    },
    ticker: {
      cbe: 'CBE Financial Core: Port 445 SMB anomaly intercepted on SERVER-04',
      ethioCert: 'Ethio-CERT Feed: Cobalt Strike C2 IP 185.220.101.5 added to perimeter blocklist',
      openSquat: 'openSquat: Rogue domain registered telebirr-verify.top (94% homoglyph score)',
      telecom: 'Ethio Telecom AS24757: Ingress scrubbed 14.8 Gbps SYN flood sweep',
      insa: 'INSA Directive 2026-04: Mandatory dual-custody enforced for all banking endpoints',
    },
    banner: {
      activeTenant: 'Active Tenant:',
      role: 'Role:',
      dataMode: 'Data:',
      dataLive: 'LIVE API',
      dataSimulated: 'SIMULATED',
      signOut: 'Sign out',
      signIn: 'Sign in',
      switchPublic: 'Switch to Public Portal View →',
      switchSoc: '← Back to SOC Dashboard',
      systemConnected: 'Live System Connected:',
      systemConnectedDesc: 'Connected to FastAPI backend & database. Real-time telemetry, incidents, and SOAR response actions are persisted.',
      demoMode: 'Simulated Demo Mode:',
      demoModeDesc: 'Backend API offline or viewing static demo. Incident metrics and containment actions are simulated locally in memory.',
      dismiss: 'Dismiss banner',
    },
    scenarios: {
      title: 'Interactive Attack Scenario Simulator',
      subtitle: 'Inject pre-packaged attack signatures into the live pipeline to demonstrate detection, AI correlation, and SOAR response:',
      ransomware: 'CBE Ransomware Outbreak',
      phishing: 'Telebirr Phishing Wave',
      ddos: 'Ethio Telecom Core DDoS',
      insider: 'Insider Credential Abuse',
      injecting: 'Injecting Scenario...',
    },
    overview: {
      title: 'National SOC Overview & Telemetry Command',
      totalIncidents: 'Active Incidents',
      criticalIncidents: 'Critical Threats',
      pendingActions: 'Pending Approvals',
      mttd: 'Mean Time to Detect (MTTD)',
      mttr: 'Mean Time to Respond (MTTR)',
      activeThreats: 'Active Threats',
      radarTitle: 'National Critical Infrastructure Threat Radar',
      radarSubtitle: 'Real-time telemetry distribution across banking, telecom, energy & government',
      liveFeedTitle: 'Live Normalized Event Stream',
      liveFeedSubtitle: 'Real-time ECS telemetry ingested from Windows endpoints, Linux servers, and network perimeter',
      allSectors: 'All Sectors',
      financial: 'Banking & Financial',
      telecom: 'Telecommunications',
      energy: 'Energy & Power Grid',
      government: 'Government & Defense',
    },
    common: {
      severity: 'Severity',
      status: 'Status',
      critical: 'CRITICAL',
      high: 'HIGH',
      medium: 'MEDIUM',
      low: 'LOW',
      info: 'INFO',
      active: 'ACTIVE',
      investigating: 'INVESTIGATING',
      contained: 'CONTAINED',
      resolved: 'RESOLVED',
      closed: 'CLOSED',
      pending: 'PENDING',
      approved: 'APPROVED',
      rejected: 'REJECTED',
      executed: 'EXECUTED',
      details: 'Details',
      actions: 'Actions',
      filter: 'Filter',
      all: 'All',
      search: 'Search...',
      refresh: 'Refresh',
      close: 'Close',
      save: 'Save Changes',
      cancel: 'Cancel',
      timestamp: 'Timestamp',
      target: 'Target Host',
      source: 'Source IP',
    },
    response: {
      title: 'SOAR Containment & Response Command Center',
      subtitle: 'Human-in-the-loop dual-custody verification for destructive mitigation playbooks',
      dualCustodyBanner: 'INSA Regulatory Compliance Notice',
      dualCustodyDesc: 'Destructive containment actions (host isolation, IP perimeter block, account lockout) strictly require dual-custody approval. An action requester cannot approve their own action.',
      pendingApprovals: 'Pending Dual-Custody Approvals',
      executedActions: 'Historical Response Audit Trail',
      approveBtn: 'Approve & Execute',
      rejectBtn: 'Reject Action',
      executeBtn: 'Execute Mitigation',
      rollbackBtn: 'Rollback Action',
      requester: 'Requested By',
      approver: 'Approved By',
      actionType: 'Action Type',
    },
    phishing: {
      title: 'Phishing Forensics & Amharic Scam Analyzer',
      subtitle: 'RFC-822 header inspection, cryptographic SPF/DKIM/DMARC verification, and native Ge\'ez NLP analysis',
      analyzeBtn: 'Analyze Email Sample',
      samplePlaceholder: 'Paste raw email RFC-822 headers or SMS lure text here...',
      spfValid: 'SPF Authentication',
      dkimValid: 'DKIM Signature',
      dmarcValid: 'DMARC Policy',
      amharicKeywordsFound: 'Amharic Financial Scam Heuristics',
      telebirrShield: 'Telebirr Brand Protection',
      riskScore: 'Aggregated Threat Risk Score',
    },
    publicPage: {
      navHome: 'Home',
      navAbout: 'About System',
      navDocs: 'Documentation',
      navContact: 'Contact INSA / CERT',
      heroBadge: 'NATIONAL CYBER RESILIENCE PLATFORM',
      heroTitle: 'Shielding Ethiopian Critical Infrastructure with',
      heroTitleHighlight: 'Autonomous AI Defense',
      heroSubtitle: 'Enterprise-grade SIEM, real-time threat intelligence, and human-in-the-loop incident response built to defend banks, telecommunications, energy networks, and public institutions.',
      ctaEnterSoc: 'Enter SOC Incident Command →',
      ctaLearnMore: 'Explore Technical White Paper',
      feature1Title: '7 Specialized AI Agents',
      feature1Desc: 'Collaborative autonomous agents performing anomaly triage, IOC correlation, root-cause investigation, and board briefings.',
      feature2Title: 'Dual-Custody SOAR Gate',
      feature2Desc: 'Strict INSA directive compliance requiring secondary security officer sign-off before isolating critical production endpoints.',
      feature3Title: 'Native Amharic Defense',
      feature3Desc: 'Specialized Ge\'ez NLP models detecting localized Telebirr mobile wallet phishing, lottery lures, and banking scams.',
      statsEps: '51,000+',
      statsEpsLabel: 'EPS SIGMA Evaluator Throughput',
      statsAgents: '7 Agents',
      statsAgentsLabel: 'Autonomous Multi-Agent Swarm',
      statsPass: '279 / 279',
      statsPassLabel: 'Automated Pytest Suite Passed',
      footerText: 'ETHIO-CYBERGUARD • Built with pride for Ethiopian and Global Cyber Resilience • Apache-2.0 License',
    },
  },
  am: {
    nav: {
      overview: 'አጠቃላይ እይታ',
      pipeline: 'የተቀናጀ የፍተሻ መስመር',
      monitoring: 'የቀጥታ ክትትል',
      incidents: 'የሳይበር አደጋዎች',
      threat_intel: 'የስጋት መረጃ',
      investigation: 'ምርመራ እና ማስረጃ',
      phishing: 'ፊሺንግ መርማሪ',
      typosquat: 'የስም ቅጅ እና ማጭበርበር',
      osint: 'የጥቃት ቀጠና ቅኝት (OSINT)',
      awareness: 'የሰራተኞች ግንዛቤ',
      assistant: 'የኤአይ ረዳት (AI Copilot)',
      risk: 'የስጋት ስሌት እና ትንተና',
      response: 'የፈጣን ምላሽ ማዕከል',
      reports: 'ሪፖርቶች እና ተገዢነት',
      settings: 'የማንነት እና ፈቃድ አስተዳደር',
      admin: 'የስርዓት አስተዳደር',
    },
    badges: {
      commonGraph: 'የጋራ ግራፍ',
      live: 'ቀጥታ',
      nlpForensics: 'የቋንቋ ትንተና',
      openSquat: 'ክፍት ቅኝት',
      spiderFoot: 'ስፓይደር ፉት',
      simulations: 'ተሞክሮ',
      sevenAgents: '7 ኤጀንቶች',
      export: 'ላክ',
    },
    header: {
      title: 'ኢትዮ-ሳይበርጋርድ',
      defcon: 'ደረጃ 2 (DEFCON 2)',
      subtitle: 'ብሄራዊ የሳይበር ደህንነት እና የአደጋ መቆጣጠሪያ • ወሳኝ መሰረተ-ልማት',
      tickerPrefix: 'የኢትዮ-ሰርት የቀጥታ ዜና፡',
      insaLink: 'የኢንሳ ግንኙነት፡ ተመሳስሏል',
      rootSoc: 'አዲስ አበባ ዋና የሳይበር ማዕከል',
      searchPlaceholder: 'አይኦሲ፣ ሲስተሞች፣ እርምጃዎችን ለመፈለግ ⌘K ይጫኑ...',
      hudShortcut: '⌘K ፈጣን ፍለጋ',
      apiLive: 'ቀጥታ ኤፒአይ',
      apiSimulated: 'የሙከራ ሁኔታ',
      apiChecking: 'በማረጋገጥ ላይ',
      ingestRate: 'መረጃ ቅበላ፡',
      muteSound: 'የታክቲካል ድምፅ ማጥፊያ',
      enableSound: 'የታክቲካል ድምፅ ማብሪያ',
      languageToggle: 'ወደ እንግሊዝኛ / አማርኛ ቀይር',
      notifications: 'ማሳወቂያዎችን ክፈት',
    },
    ticker: {
      cbe: 'የኢትዮጵያ ንግድ ባንክ፡ በSERVER-04 ላይ የፖርት 445 SMB ያልተለመደ እንቅስቃሴ ተጨናገፈ',
      ethioCert: 'የኢትዮ-ሰርት መረጃ፡ የCobalt Strike C2 አይፒ 185.220.101.5 ወደ እግድ ዝርዝር ተካተተ',
      openSquat: 'openSquat፡ አደገኛ የውሸት ድረ-ገጽ telebirr-verify.top ተመዘገበ (94% የማስመሰል ነጥብ)',
      telecom: 'ኢትዮ ቴሌኮም AS24757፡ የ14.8 Gbps የSYN ጎርፍ ጥቃት ሙሉ በሙሉ ተመከተ',
      insa: 'የኢንሳ መመሪያ 2026-04፡ በሁሉም የባንክ ሲስተሞች ላይ ባለሁለት-ደረጃ ማጽደቅ ግዴታ ነው',
    },
    banner: {
      activeTenant: 'ንቁ ተቋም፡',
      role: 'ሚና፡',
      dataMode: 'የመረጃ ሁኔታ፡',
      dataLive: 'ቀጥታ ኤፒአይ',
      dataSimulated: 'የሙከራ',
      signOut: 'ውጣ',
      signIn: 'ግባ',
      switchPublic: 'ወደ ህዝባዊ ፖርታል ተቀይር →',
      switchSoc: '← ወደ ሳይበር ቁጥጥር ማዕከል ተመለስ',
      systemConnected: 'የቀጥታ ስርዓት ተገናኝቷል፡',
      systemConnectedDesc: 'ከFastAPI ሰርቨር እና ዳታቤዝ ጋር ተገናኝቷል። የቀጥታ ቴሌሜትሪ፣ አደጋዎች እና የመከላከያ እርምጃዎች በቋሚነት ይመዘገባሉ።',
      demoMode: 'የማስመሰያ ሙከራ ሁኔታ፡',
      demoModeDesc: 'ሰርቨሩ ከመስመር ውጭ ነው ወይም የማሳያ ገጽ እየተመለከቱ ነው። መረጃዎች እና እርምጃዎች በማስታወሻ ውስጥ በሙከራ ይሰራሉ።',
      dismiss: 'ባነሩን ዝጋ',
    },
    scenarios: {
      title: 'የጥቃት እና የአደጋ ማስመሰያ ፈተና',
      subtitle: 'የመከላከል፣ የአርቴፊሻል ኢንተለጀንስ ትንተና እና ፈጣን ምላሽን ለመፈተሽ አስቀድመው የተዘጋጁ የጥቃት ምልክቶችን ወደ ሲስተሙ ያስገቡ፡',
      ransomware: 'የንግድ ባንክ የቤዛ ጠያቂ ቫይረስ ጥቃት (Ransomware)',
      phishing: 'የቴሌብር አጭበርባሪ ፊሺንግ (SMS Phishing)',
      ddos: 'የኢትዮ ቴሌኮም የመረብ ማጨናነቅ ጥቃት (DDoS)',
      insider: 'የውስጥ ሰራተኛ የተፈቀደ መረጃ አላግባብ መጠቀም',
      injecting: 'ጥቃቱን በማስገባት ላይ...',
    },
    overview: {
      title: 'ብሄራዊ የሳይበር ክትትል እና ቴሌሜትሪ ትዕዛዝ ማዕከል',
      totalIncidents: 'ንቁ የሳይበር አደጋዎች',
      criticalIncidents: 'አስቸኳይ እና ከፍተኛ አደጋዎች',
      pendingActions: 'ያልጸደቁ የመከላከያ እርምጃዎች',
      mttd: 'አደጋን የመለየት አማካይ ፍጥነት (MTTD)',
      mttr: 'አደጋን የማስወገድ አማካይ ፍጥነት (MTTR)',
      activeThreats: 'ንቁ ስጋቶች',
      radarTitle: 'የኢትዮጵያ ወሳኝ መሰረተ-ልማቶች የሳይበር ራዳር',
      radarSubtitle: 'በባንክ፣ ቴሌኮም፣ ሃይል እና የመንግስት ተቋማት ላይ ያለው የጥቃት እንቅስቃሴ ስርጭት',
      liveFeedTitle: 'የቀጥታ የተጣራ የቴሌሜትሪ መረጃ ፍሰት',
      liveFeedSubtitle: 'ከዊንዶውስ፣ ሊኑክስ እና የኔትወርክ መከላከያዎች በቅጽበት የተሰበሰቡ የደህንነት ክስተቶች',
      allSectors: 'ሁሉም ዘርፎች',
      financial: 'ባንክ እና ፋይናንስ',
      telecom: 'ቴሌኮሙኒኬሽን',
      energy: 'የኤሌክትሪክ ሃይል ማመንጫ',
      government: 'መንግስት እና መከላከያ',
    },
    common: {
      severity: 'ክብደት',
      status: 'ሁኔታ',
      critical: 'አስቸኳይ',
      high: 'ከፍተኛ',
      medium: 'መካከለኛ',
      low: 'ዝቅተኛ',
      info: 'መረጃ',
      active: 'ንቁ',
      investigating: 'በምርመራ ላይ',
      contained: 'የተገታ',
      resolved: 'የተፈታ',
      closed: 'የተዘጋ',
      pending: 'ውሳኔ የሚጠብቅ',
      approved: 'የጸደቀ',
      rejected: 'ውድቅ የተደረገ',
      executed: 'የተፈጸመ',
      details: 'ዝርዝር መረጃ',
      actions: 'እርምጃዎች',
      filter: 'አጣራ',
      all: 'ሁሉም',
      search: 'ፈልግ...',
      refresh: 'አድስ',
      close: 'ዝጋ',
      save: 'ለውጦችን መዝግብ',
      cancel: 'ይቅር',
      timestamp: 'የተከሰተበት ጊዜ',
      target: 'የተጠቃው ሲስተም',
      source: 'የአጥቂው አይፒ',
    },
    response: {
      title: 'የፈጣን ምላሽ እና አደጋ መቆጣጠሪያ ማዕከል (SOAR)',
      subtitle: 'አደገኛ የሳይበር ጥቃቶችን ለመከላከል ባለሁለት-ደረጃ የሰው ማረጋገጫ እና አውቶማቲክ መከላከያ',
      dualCustodyBanner: 'የኢንሳ የሳይበር ደህንነት መመሪያ ማሳሰቢያ',
      dualCustodyDesc: 'ወሳኝ ሲስተሞችን ከኔትወርክ ማግለል፣ አይፒ አድራሻን ማገድ እና አካውንት ማገድን የመሳሰሉ እርምጃዎች በሁለት የደህንነት ባለሙያዎች መጽደቅ አለባቸው። እርምጃውን የጠየቀ ባለሙያ ራሱ ማጽደቅ አይችልም።',
      pendingApprovals: 'ውሳኔ የሚጠብቁ ባለሁለት-ደረጃ ማጽደቂያዎች',
      executedActions: 'የተወሰዱ የመከላከያ እርምጃዎች የኦዲት መዝገብ',
      approveBtn: 'አጽድቅ እና ፈጽም',
      rejectBtn: 'እርምጃውን ውድቅ አድርግ',
      executeBtn: 'እርምጃውን ፈጽም',
      rollbackBtn: 'እርምጃውን ወደ ነበረበት መልስ',
      requester: 'የጠየቀው ባለሙያ',
      approver: 'ያጸደቀው ኃላፊ',
      actionType: 'የእርምጃው አይነት',
    },
    phishing: {
      title: 'የፊሺንግ ፎረንሲክስ እና የአማርኛ ማጭበርበሪያዎች መርማሪ',
      subtitle: 'የኢሜይል ሄደር ምርመራ፣ የSPF/DKIM/DMARC ዲጂታል ፊርማ ማረጋገጫ እና የሀገር ውስጥ የአማርኛ ቃላት ትንተና',
      analyzeBtn: 'የኢሜይል ወይም ኤስኤምኤስ ናሙና ፈትሽ',
      samplePlaceholder: 'የተጠረጠረውን የኢሜይል ሄደር ወይም የአማርኛ የማጭበርበሪያ መልዕክት እዚህ ይለጥፉ...',
      spfValid: 'የSPF ህጋዊነት ማረጋገጫ',
      dkimValid: 'የDKIM ዲጂታል ፊርማ',
      dmarcValid: 'የDMARC መመሪያ ተገዢነት',
      amharicKeywordsFound: 'የተገኙ የአማርኛ ማጭበርበሪያ ቃላት',
      telebirrShield: 'የቴሌብር ብራንድ ጥበቃ ጋሻ',
      riskScore: 'የስጋት ደረጃ ስሌት',
    },
    publicPage: {
      navHome: 'መነሻ',
      navAbout: 'ስለ ሲስተሙ',
      navDocs: 'ቴክኒካል ሰነዶች',
      navContact: 'ኢንሳ / ኢትዮ-ሰርት',
      heroBadge: 'ብሄራዊ የሳይበር ደህንነት እና ጥበቃ መድረክ',
      heroTitle: 'የኢትዮጵያን ወሳኝ መሰረተ-ልማቶች በጥበቃ ስር ማዋል በ',
      heroTitleHighlight: 'አውቶማቲክ አርቴፊሻል ኢንተለጀንስ',
      heroSubtitle: 'የላቀ የሳይበር ቁጥጥር ማዕከል (SIEM)፣ የቀጥታ የጥቃት መረጃ እና የሰለጠኑ ባለሙያዎች ፈጣን ምላሽ — ለባንኮች፣ ቴሌኮም፣ የኤሌክትሪክ ሃይል እና ለመንግስት ተቋማት የተዘጋጀ ብሄራዊ ጋሻ።',
      ctaEnterSoc: 'ወደ ሳይበር ቁጥጥር ማዕከል ይግቡ →',
      ctaLearnMore: 'የቴክኒካል ጥናት ሰነዱን ያንብቡ',
      feature1Title: '7 ልዩ የኤአይ ወኪሎች (AI Agents)',
      feature1Desc: 'የሳይበር ጥቃቶችን በቅጽበት የሚመረምሩ፣ መነሻቸውን የሚያጣሩ እና ለአመራሮች ፈጣን ሪፖርት የሚያቀርቡ ብልህ ወኪሎች።',
      feature2Title: 'ባለሁለት-ደረጃ ማጽደቂያ (Dual-Custody)',
      feature2Desc: 'የኢንሳን መመሪያ በጥብቅ በማክበር ወሳኝ የባንክ እና የቴሌኮም ሰርቨሮችን ከኔትወርክ ከማግለል በፊት ሁለት ባለሙያዎች እንዲያረጋግጡ ያስገድዳል።',
      feature3Title: 'ሀገር በቀል የአማርኛ ቋንቋ ጥበቃ',
      feature3Desc: 'የቴሌብር እና የኢትዮጵያ ንግድ ባንክን ስም ተጠቅመው የሚላኩ የውሸት የኤስኤምኤስ እና የኢሜይል ማጭበርበሪያዎችን በግዕዝ ፊደላት ፈትሾ የሚለይ ሞዴል።',
      statsEps: '51,000+',
      statsEpsLabel: 'በሰከንድ የሚጣሩ የደህንነት መረጃዎች (EPS)',
      statsAgents: '7 ኤጀንቶች',
      statsAgentsLabel: 'የተቀናጁ ራሳቸውን የቻሉ የኤአይ ወኪሎች',
      statsPass: '279 / 279',
      statsPassLabel: 'የተረጋገጡ አውቶማቲክ የሶፍትዌር ፈተናዎች',
      footerText: 'ኢትዮ-ሳይበርጋርድ (ETHIO-CYBERGUARD) • ለኢትዮጵያ እና ለአለም አቀፍ የሳይበር ደህንነት በኩራት የተገነባ • Apache-2.0 ፈቃድ',
    },
  },
};

/**
 * Returns translation dictionary for given language with English fallback.
 */
export function getTranslations(lang: Language = 'en'): TranslationDictionary {
  return TRANSLATIONS[lang] || TRANSLATIONS.en;
}
