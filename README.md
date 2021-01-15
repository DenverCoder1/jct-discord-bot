# JCT Discord Bot

Bot for JCT ESP CompSci Discord server

## Contributors

This bot was created by the contribution of the following members. If you would like to contribute, please be in touch with one of the current contributors and then take a look at [the contributing guide](contributing.md)

<!-- readme: contributors -start -->
<table>
<tr>
    <td align="center">
        <a href="https://github.com/abrahammurciano">
            <img src="https://avatars1.githubusercontent.com/u/25041135?v=4" width="100;" alt="abrahammurciano"/>
            <br />
            <sub><b>Abraham Murciano</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/PSilver22">
            <img src="https://avatars1.githubusercontent.com/u/75566318?v=4" width="100;" alt="PSilver22"/>
            <br />
            <sub><b>PSilver22</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/DenverCoder1">
            <img src="https://avatars0.githubusercontent.com/u/20955511?v=4" width="100;" alt="DenverCoder1"/>
            <br />
            <sub><b>Jonah Lawrence</b></sub>
        </a>
    </td></tr>
</table>
<!-- readme: contributors -end -->

## Issues and Feature Requests

If you'd like a new feature added to the bot, or you have discovered some misbehaviour by it, please feel free to open an issue detailing it in the [GitHub issues tab](https://https://github.com/DenverCoder1/jct-discord-bot/issues).

## Features

### Commands

Here is a list of the available commands the bot responds to and how it does so.

#### ++logs

Replies with an extract from the error log file.

#### ++help

Replies with a list of available commands.

#### ++join first name, last name, campus, year

Assigns the user a role based on their campus and year. Assigns them their name as a nickname. Replaces their Unassigned role with the Assigned role. Once this is done, the bot will introduce them to everyone else in the welcome channel.

#### ++piglatin lots of words

This command will reply with your message _lots of words_ but in pig latin.

#### ++ping

This command does just what you'd think it does. When a user types `++ping` into a channel which the bot is in, the bot will respond with a message to acknowledge your ping.

### Automated Tasks

This is a list of the tasks that the bot performs automatically based on some event.

#### New User

When a user joins, they are given the Unassigned role, greeted by the bot, and asked to introduce themselves with the join command.

#### Role Tags

A role can be given a tag by naming it something of the form **_Name_ | _tag_**. All members of the role will now have _tag_ in their server nickname. Users can have multiple tags.
