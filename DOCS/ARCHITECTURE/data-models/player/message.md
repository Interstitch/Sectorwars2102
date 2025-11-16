# Message Data Definition

## Overview

The Message system in Sector Wars 2102 enables communication between players, teams, and the game system. It supports private conversations, team coordination, and system notifications. The messaging system is critical for social interaction, strategic planning, and delivering important game information to players.

**Note**: The current implementation supports basic messaging with threading. Advanced features like attachments, coordinate sharing, templates, and encryption are planned for future releases.

## Data Model

```typescript
// Message types (simplified from original design)
export enum MessageType {
  PLAYER = "player",       // Direct player-to-player messages
  TEAM = "team",           // Team chat and announcements
  SYSTEM = "system"        // Game system notifications
}

// Note: Original design included 9 types (faction broadcasts, sector broadcasts, etc.)
// but implementation currently supports these 3 core types.

export enum MessagePriority {
  LOW = "low",             // Routine information
  NORMAL = "normal",       // Standard priority (default)
  HIGH = "high",           // Important messages
  URGENT = "urgent"        // Critical alerts
}

// Note: Actual implementation uses lowercase string values, not uppercase enums

export enum MessageStatus {
  UNREAD = "UNREAD",       // Not yet viewed (no read_at timestamp)
  READ = "READ",           // Viewed by recipient (has read_at timestamp)
  DELETED = "DELETED"      // Marked for deletion (soft delete flags)
}

// Attachments, Coordinates, and Templates interfaces removed - not implemented yet
// These are planned features for future development

export interface MessageModel {
  id: string;                                  // Unique identifier (UUID)

  // Sender and recipient information
  sender_id: string;                           // Player ID who sent message (UUID)
  recipient_id: string | null;                 // Player ID of recipient (null for team messages)
  team_id: string | null;                      // Team ID (null for direct messages)

  // Message content
  subject: string | null;                      // Message title/subject (max 255 chars)
  content: string;                             // Main message content (Text field)

  // Message metadata
  sent_at: Date;                               // When message was sent
  read_at: Date | null;                        // When message was read (null if unread)

  // Soft deletion flags
  deleted_by_sender: boolean;                  // Whether sender deleted message
  deleted_by_recipient: boolean;               // Whether recipient deleted message

  // Threading support
  thread_id: string | null;                    // For conversation threads (UUID)
  reply_to_id: string | null;                  // For direct replies (UUID)

  // Message type and flags
  message_type: string;                        // 'player', 'team', or 'system' (default: 'player')
  priority: string;                            // 'low', 'normal', 'high', 'urgent' (default: 'normal')

  // Moderation flags (for abuse prevention)
  flagged: boolean;                            // Whether message has been flagged
  flagged_reason: string | null;               // Reason for flagging
  moderated_at: Date | null;                   // When moderation occurred
  moderated_by: string | null;                 // User ID of moderator (UUID)

  // Relationships (loaded when needed)
  sender?: Player;                             // Sender player object
  recipient?: Player;                          // Recipient player object
  team?: Team;                                 // Team object for team messages
  reply_to?: MessageModel;                     // Parent message if this is a reply
  replies?: MessageModel[];                    // Child replies to this message
  moderator?: User;                            // Moderator user object
}

// Note: Advanced features not yet implemented:
// - Attachments (files, images, coordinates)
// - Message templates
// - Encryption
// - CC recipients
// - Expiration dates
// - Rich formatting (HTML)

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