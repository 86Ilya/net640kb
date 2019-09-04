# 640Kb ought to be enough for anyone

___This article is devoted to final work on the Python Developer course.___
[Russian version](article_ru.md)

&nbsp; &nbsp; &nbsp;Nowadays, looking at the flow of information around us, we can confidently say that Orwell was wrong, and Huxley was right. Incredible amount of garbage in this stream makes it difficult to see valuable information. Interesting news overloaded by heavy scripts, forms, popups.

&nbsp; &nbsp; &nbsp;During one day humanity make as many photos as we did ten-fifteen years ago. Multiply it on average size of photo one megabyte and you will get awful amount unusable information; size of the Bible is one and half megabyte. I don't believe that your post with photo of morning coffee together with comments have more significance.

&nbsp; &nbsp; &nbsp;Think about how many resources is necessary for maintenance this traffic. Processors, disks, electricity. You can argue that this consumption are providing growth of technical innovations. I agree with you, but technical innovations for what? We are still flying into space on processors with frequency 200Mhz, it is ten times lower than in your smartphone!

&nbsp; &nbsp; &nbsp;How much we are talking about using resources wisely, about recycling. Is it time to set eyes on using resources in IT?

&nbsp; &nbsp; &nbsp;In the same time, this behavior in consumption caused bad style in software development. Look deeper into the code, that programmers did: if earlier in school we were scolded for forgotten "free" method, that today it's normal to include libraries just because one function. Scold garbage collectors — a relentless trend. Therefore, we get an application with functionality slightly more complicated than a notebook and memory consumption of 60-70 gigabytes. Sooner or later this problem will become actual, but who will be ready for rewriting tonnes of code in working processes? Even now adding of new features to working system is like surgical operation. How difficult will be full code rewriting?

&nbsp; &nbsp; &nbsp;My application is not panacea for all ills, but it's call to pay attention to limited resources. Think about consumption. The essence of service is very simple — it's social network with familiar functions: viewing and adding news, chatting with friends, adding likes. But there are one restriction: you have only 640Kb for all-purpose. And not only for the content itself, it also includes what is not visible to the eye. Nobody thinks about how many resources are consumed by "Hell"message. It's only 5 bytes. But on other languages it will be message in UTF-8, so each symbol can take 2 or 4 bytes itself. How many rows and columns in database are affected by adding this message? At a minimum: record ID and link to message owner. It's a Metropolise" of IT world, and we have to pay for it with you.

&nbsp; &nbsp; &nbsp;The app has obvious advantages:
 - The maximum user page size is known in advance. So it's easy to calculate resources for maintenance. Let's say we have 3 billion users. It's 1,92×10¹² Kb or 1788Tb of data. Enormous numeral, rent per month for such quantities in cloud will cost as apartment in Moscow. But it's still less than existing solutions.
 - "Nonlinear likes". Everything in this application have its own weight, so likes are not an exception. Each "like"
subtract few bytes from your page size. And algorithm of calculating "likes" have dependence with your page size. Then more your page then less your likes costs.
 - Spam defense. Whatever one may say, the user cannot send more messages than 640Kb.

#### Technical components of the project is pretty simple.

The following is used in backend:
 - The basis is the Django framework in conjunction with the Postgresql database.
 - Channels and Redis are used to exchange messages between users.
 - Each user also has his own "update flow" channel, through which he receives messages about new events and changes in the size of his page.

On the frontend:
 - Bootstrap 4.0 as the main set of style templates
 - Vue.js for interactive user interaction.
 - Websocket to communicate with channels

There are also disadvantages:
 - It's impossible to tell others about your vacations, because one FullHD photo need space twice bigger than you are allowed.
 - It's impossible to add millions of friends. You’ll are limited to people you are really interested in.

Currently unrealized the following ideas:
 - Storage of the user's page size in the key-value store for faster access. At the moment, when a page size is requested, a full recalculation takes place, and this is a time-consuming operation.
 - ASCII ART. If we are talking about modest consumption, then it would be appropriate to use the ascii-art as pictures.
 - Page layout. At now the application is optimized for only one browser and only for the desktop. Optimizing CSS rules has never been my forte, but this is a solvable question.
