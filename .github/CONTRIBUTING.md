# Contributing to PerfectFrameAI
👍🎉 First off, thanks for taking the time to contribute! 🎉👍
Following these guidelines helps to communicate that you respect the time of the developers
managing and developing this open source project. In return, they should reciprocate that respect
in addressing your issue, assessing changes, and helping you finalize your pull requests.

> Note:
>
> I am still learning how to be an effective maintainer for our project. I am committed to improving, so please feel free to share any feedback or suggestions you might have. Thank you!

PerfectFrameAI is an open source project and we love to receive contributions from our community — you!
There are many ways to contribute, from writing tutorials or blog posts, improving the documentation, 
submitting bug reports and feature requests or writing code which can be incorporated into PerfectFrameAI itself.

## Code of Conduct
This project and everyone participating in it is governed by this ![Code of Conduct](CODE_OF_CONDUCT).
By participating, you are expected to uphold this code. 

## I don't want to read this whole thing I just have a question
Please use discussion tab for this.

## Creating an Issue
Before **creating** an Issue for `features`/`bugs`/`improvements` please follow these steps:
1. **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/BKDDFS/PerfectFrameAI/issues).
1. If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/BKDDFS/PerfectFrameAI/issues/new).
Be sure to include a **title and clear description**, as much relevant information as possible.
Please select the correct Issue type, for example `bug` or `feature`.
1. all Issues are automatically given the label `status: waiting for triage`
1. if you wish to work on the Issue once it has been triaged and label changed to `status: ready for dev`, 
please include this in your Issue description

## Working on an Issue
Before working on an existing Issue please follow these steps:
1. only ask to be assigned 1 **open** issue at a time
1. look out for the Issue label `status: ready for dev` (if it does not have this label, your work might not be accepted)
1. comment asking for the issue to be assigned to you (do not tag maintainers on GitHub as all maintainers receive your comment notifications)
1. after the Issue is assigned to you, you can start working on it
1. **only** start working on this Issue (and open a Pull Request) when it has been assigned to you - this will prevent confusion, multiple people working on the same issue and work not being used
1. do **not** enable GitHub Actions on your fork
1. reference the Issue in your Pull Request (for example `closes #123`)
1. please do **not** force push to your PR branch, this makes it very difficult to re-review - commits will be squashed when merged

## Coding Guidelines:
- **Remember** that for the part operating outside of the Docker container, the following conventions have been adopted:
1. Only internal Python libraries may be used.
1. The code should be executable for at least Python version 3.7.
- Make sure that you write tests for your code.
- Make sure you write docstrings for your code.
- Make sure your code follows PEP8 standards.

> Notes:
>
> - it is not sustainable for maintainers to review historical comments asking for assignments
before the Issue label `status: ready for dev` was added;
only requests for assignment of an Issue after this label has been added will be considered
> - check the `Assignees` box at the top of the page to see if the issue has been assigned
to someone else before requesting this be assigned to you
> - if an Issue is unclear, ask questions to get more clarity before asking to have the Issue assigned to you
> - only request to be assigned an Issue if you know how to work on it
> - an Issue can be assigned to multiple people,
if you all agree to collaborate on the issue
> - any Issues that have no activity after 2 weeks will be unassigned and re-assigned to someone else

## Reviewing Pull Requests
We welcome everyone to review Pull Requests, it is a great way to learn, network and support each other.
