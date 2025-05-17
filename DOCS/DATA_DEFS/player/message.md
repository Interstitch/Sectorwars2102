# Message Data Definition

## Overview

The Message system in Sector Wars 2102 enables communication between players, teams, and the game system. It supports private conversations, team coordination, faction announcements, and system notifications. The messaging system is critical for social interaction, strategic planning, and delivering important game information to players.

## Data Model

```typescript
export enum MessageType {
  PLAYER_TO_PLAYER = "PLAYER_TO_PLAYER",       // Direct player messages
  TEAM_MESSAGE = "TEAM_MESSAGE",               // Team chat/announcements
  SYSTEM_NOTIFICATION = "SYSTEM_NOTIFICATION", // Game system alerts
  FACTION_BROADCAST = "FACTION_BROADCAST",     // Messages from factions
  SECTOR_BROADCAST = "SECTOR_BROADCAST",       // Local sector communication
  MISSION_COMMUNICATION = "MISSION_COMMUNICATION", // Mission-related messages
  MARKET_ALERT = "MARKET_ALERT",               // Trading opportunities
  COMBAT_REPORT = "COMBAT_REPORT",             // Battle summaries
  NEWS_BULLETIN = "NEWS_BULLETIN"              // Galaxy news updates
}

export enum MessagePriority {
  LOW = "LOW",                                 // Routine information
  NORMAL = "NORMAL",                           // Standard priority
  HIGH = "HIGH",                               // Important messages
  URGENT = "URGENT",                           // Critical alerts
  EMERGENCY = "EMERGENCY"                      // Highest priority
}

export enum MessageStatus {
  UNREAD = "UNREAD",                           // Not yet viewed
  READ = "READ",                               // Viewed by recipient
  ARCHIVED = "ARCHIVED",                       // Stored for later
  DELETED = "DELETED",                         // Marked for deletion
  EXPIRED = "EXPIRED"                          // No longer accessible
}

export interface MessageAttachment {
  type: string;                                // Attachment type
  name: string;                                // Attachment name
  content_id: string;                          // Reference to content
  size: number;                                // Size in bytes
  mime_type: string;                           // Content format
  preview_text: string;                        // Short preview
  requires_download: boolean;                  // Whether needs separate download
}

export interface MessageCoordinates {
  sector_id: number;                           // Referenced sector
  cluster_id?: string;                         // Referenced cluster
  region_id?: string;                          // Referenced region
  x: number;                                   // X coordinate
  y: number;                                   // Y coordinate
  z: number;                                   // Z coordinate
  label: string;                               // Location description
}

export interface MessageSender {
  entity_type: string;                         // "player", "system", "faction", etc.
  entity_id: string;                           // Sender identifier
  name: string;                                // Display name
  avatar_url?: string;                         // Sender image
  faction_id?: string;                         // Associated faction
  is_verified: boolean;                        // Whether identity confirmed
}

export interface MessageRecipient {
  entity_type: string;                         // "player", "team", "all", etc.
  entity_id: string;                           // Recipient identifier
  name: string;                                // Display name
  received_at?: Date;                          // When delivered to recipient
  read_at?: Date;                              // When read by recipient
  status: MessageStatus;                       // Current message status
}

export interface TemplateVariable {
  key: string;                                 // Variable name
  value: string;                               // Replacement value
  format?: string;                             // Formatting instructions
}

export interface MessageModel {
  id: string;                                  // Unique identifier
  message_type: MessageType;                   // Message classification
  priority: MessagePriority;                   // Importance level
  created_at: Date;                            // When message was created
  expires_at?: Date;                           // When message becomes invalid
  
  // Content
  subject: string;                             // Message title/subject
  body: string;                                // Main message content
  formatted_body?: string;                     // HTML version if applicable
  is_encrypted: boolean;                       // Whether content is encrypted
  language_code: string;                       // ISO language code
  
  // Participants
  sender: MessageSender;                       // Who sent the message
  recipients: MessageRecipient[];              // Who received the message
  cc_recipients?: MessageRecipient[];          // Carbon copy recipients
  reply_to_id?: string;                        // Parent message if a reply
  
  // Supplementary Content
  attachments: MessageAttachment[];            // Files/content attached
  links: string[];                             // URLs referenced
  coordinates?: MessageCoordinates[];          // Locations referenced
  
  // Metadata
  tags: string[];                              // Categorization labels
  template_id?: string;                        // If based on template
  template_variables?: TemplateVariable[];     // Template customization
  message_chain_id?: string;                   // Conversation grouping
  
  // System Flags
  requires_confirmation: boolean;              // Whether needs acknowledgment
  is_automated: boolean;                       // Whether sent by system
  allows_replies: boolean;                     // Whether replies permitted
  importance_flag: boolean;                    // User-marked important
}

export interface MessageTemplate {
  id: string;                                  // Template identifier
  name: string;                                // Template name
  description: string;                         // Template purpose
  subject_template: string;                    // Subject with variables
  body_template: string;                       // Body with variables
  available_variables: {                       // Variables that can be used
    key: string;
    description: string;
    default_value: string;
    validation_regex?: string;                 // Validation pattern
  }[];
  message_type: MessageType;                   // Default message type
  priority: MessagePriority;                   // Default priority
  category: string;                            // Template category
  is_system_template: boolean;                 // Whether system-defined
}

export interface ConversationSummary {
  conversation_id: string;                     // Unique thread identifier
  participants: string[];                      // Participant identifiers
  participant_names: string[];                 // Display names
  message_count: number;                       // Messages in thread
  unread_count: number;                        // Unread messages
  latest_message: {                            // Most recent message
    sender_name: string;
    subject: string;
    snippet: string;                           // Content preview
    sent_at: Date;
  };
  first_message_at: Date;                      // Thread start time
  last_message_at: Date;                       // Thread last activity
  is_archived: boolean;                        // Whether archived
}

export interface MessageFilter {
  sender_ids?: string[];                       // Filter by senders
  recipient_ids?: string[];                    // Filter by recipients
  message_types?: MessageType[];               // Filter by type
  date_range?: {                               // Filter by date
    start: Date;
    end: Date;
  };
  status?: MessageStatus[];                    // Filter by status
  search_text?: string;                        // Text search
  has_attachments?: boolean;                   // Filter by attachments
  priority_minimum?: MessagePriority;          // Filter by priority
  tags?: string[];                             // Filter by tags
  conversation_id?: string;                    // Filter by thread
}

export interface MessageStatistics {
  player_id: string;                           // Player ID
  unread_count: number;                        // Total unread messages
  by_type: {                                   // Count by type
    [messageType: string]: number;
  };
  by_sender: {                                 // Count by sender
    [senderId: string]: number;
  };
  by_priority: {                               // Count by priority
    [priority: string]: number;
  };
  received_today: number;                      // Messages received today
  sent_today: number;                          // Messages sent today
  most_frequent_contacts: {                    // Common correspondents
    entity_id: string;
    name: string;
    message_count: number;
  }[];
}
```

## Message System Features

1. **Private Messaging**: Direct communication between players
2. **Team Communication**: Group chat for coordinated operations
3. **System Notifications**: Game events and important alerts
4. **Faction Communications**: Messages from faction representatives
5. **Location Sharing**: Ability to share coordinates and locations
6. **Attachments**: Support for different types of message attachments
7. **Templates**: Pre-defined message formats for common communications
8. **Conversation Threading**: Grouping related messages together
9. **Filters and Search**: Tools to organize and find messages
10. **Read Receipts**: Tracking of message delivery and viewing

## Message Types and Usage

### Player-to-Player Messages
- Direct private communication between players
- Support for text, coordinates, and attachments
- Thread-based conversation tracking
- Customizable priority levels

### Team Messages
- Group communications for team members
- Announcements and coordination
- Role-based permissions for team broadcasts
- Persistent team chat history

### System Notifications
- Game event alerts
- Account and security notifications
- Achievement unlocks and progress updates
- Maintenance and update announcements

### Faction Broadcasts
- Messages from faction NPCs
- Faction mission opportunities
- Territory and influence updates
- Political and diplomatic announcements

### Sector Broadcasts
- Local communications to all players in a sector
- Emergency distress signals
- Trading and opportunity announcements
- Territorial claims and warnings

## Message Security and Privacy

1. **Encryption**: Optional message encryption for sensitive communications
2. **Blocking**: Ability to block unwanted senders
3. **Reporting**: System for reporting abusive messages
4. **Privacy Controls**: Settings to control who can send messages
5. **Anti-Spam**: Rate limits and filtering for mass communications

## Notification Integration

1. **In-Game Alerts**: Real-time notification of important messages
2. **Priority System**: Different notification levels based on urgency
3. **Configurable Alerts**: User control over notification behavior
4. **Cross-Device Sync**: Consistent message state across play sessions
5. **Digest Options**: Summarized notifications for frequent events

## Data Retention and Management

1. **Auto-Archiving**: Automatic archiving of old messages
2. **Expiration Policies**: Time-based message expiration
3. **Storage Quotas**: Limits on message storage per player
4. **Backup Options**: Message export and backup capabilities
5. **Message Recovery**: Retrieval of recently deleted messages