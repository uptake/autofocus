DRAFT ONLY--DO NOT QUOTE

# ShopRunner Data Science for Good: Automating Urban Wildlife Classification

![coyote](https://github.com/uptake/autofocus/raw/master/gallery/coyote1.jpg) 
<!--TK image caption formatting-->
Software developed by data scientists at ShopRunner and Uptake supports the work of urban wildlife researchers by automatically classifying images taken by motion-activated cameras, such as this image of a coyote in the Chicago area.

The growth of cities threatens animal species that do not adapt well to urban environments. **The Lincoln Park Zoo's Urban Wildlife Institute studies how urbanization affects wildlife in part by collecting images from motion-activated cameras**, beginning in 2010 around Chicago but now from more than twenty urban areas. For almost a decade, volunteers have been helping in their efforts by identifying the animal species that appear in each of those images in the online [Zooniverse](https://www.zooniverse.org/projects/zooniverse/chicago-wildlife-watch) crowdsourcing platform. However, the rate of image collection now exceeds the rate of image labeling. The information that the images contain is effectively unavailable to researchers until they have been labeled, so **image labeling has become a bottleneck that holds back their research.**

Fortunately, it is now possible to create computer programs that label images with accuracy comparable to that of humans. Moreover, ShopRunner's data science team has experience building such programs to classify products across ShopRunner's retail network for its marketplace app District. For over two years, **data scientists from ShopRunner and Uptake have been working with the Urban Wildlife Institute to use automated image classification techniques to unblock the institute's research efforts.** 

**The data and code used for this project are [publicly available](https://github.com/uptake/autofocus) so that anyone interested in developing the relevant skills can get involved.**

## Impact

> It was like they gifted us 10 interns who could work around the clock. Autofocus enables us to get on top of our backlog of images and deliver valuable insights on local wildlife now.
>
> --Urban Wildlife Institute researcher Mason Fidino, PhD <!--TK image of Mason-->

Approximately 10-15 percent of the images that the Urban Wildlife Institute's cameras capture contain humans rather than the wildlife that is relevant to the institute's research. Those images are a major nuisance because the institute wishes to respect privacy by filtering out those images before posting the rest online for volunteers to label.

![](human_example.JPG)
<!--TK image caption formatting-->
The Urban Wildlife Institute's cameras often capture images of people jogging or walking dogs, or (as in this case) images of the researchers themselves stopping by to service them.

To address this problem, Uptake's philanthropic arm Uptake.org developed the first version of a program called Autofocus that can classify an image as containing a human or not. That program proved to be sufficiently accurate to remove approximately 50% of human-containing images with a negligible rate of false positives. **On one batch of images from Spring 2016, the Urban Wildlife Institude was able to use that model to filter out roughly 3,700 images.** "It was like they gifted us 10 interns who could work around the clock," said Urban Wildlife Institute researcher Mason Fidino. "Autofocus enables us to get on top of our backlog of images and deliver valuable insights on local wildlife now."

**Data scientists at ShopRunner contributed to a second version of Autofocus that not only appears to increase human label accuracy, but also provides labels for eighteen additional kinds of animals.** The accuracy of that second version is currently under review, but preliminary results suggest that it is sufficient to automate classification of a large percentage of incoming images at least for common animal types such as deer and raccoons, further improving the speed of the Urban Wildlife Institute's research.

## Methods

![](https://brooksbrothers.scene7.com/is/image/BrooksBrothers/SX00251_HEATHER-GREY?$bbproductimages$)
<!--TK get a fashion image that we definitely have permission to use and adjust caption accordingly-->
<!--TK image caption formatting-->
ShopRunner data scientists repurposed for Autofocus work that they did to develop a system that can classify this image as showing a gray, melange, knee-length, sleeveless dress for ShopRunner's iOS shopping app District.

The Autofocus image classification model uses techniques from *deep learning*, an area of artificial intelligence that allows computers to learn how to perform tasks such as labeling images from examples rather than through explicit rules. Deep learning models for image classification have been known to provide greater accuracy than trained humans on public benchmark datasets.

ShopRunner uses deep learning image classification along with text classification models internally to place products from across its large retailer network into one set of categories so that users of its iOS app District can shop across that network in one convenient interface. Applying the same techniques to Autofocus allows its data scientists to hone their skills further in a way that has the potential to foster healthy ecosystems.

## How You Can Help

![](https://zooniverseblog.files.wordpress.com/2012/12/elephants-at-sunrise.jpg)
<!--TK get a camera trap image clearly not from Chicago that we definitely have permission to use-->
<!--TK image caption formatting-->
Further work on Autofocus could allow it to do more to support researchers by improving its accuracy and expanding its geographic scope

The current version of the Autofocus software was developed using tens of thousands of images from two summers in the Chicago area. The biggest opportunity for increasing the project's impact is to use more images from a broader range of seasons and locations so that the model can be used more broadly. Data scientists at ShopRunner are currently working with the Urban Wildlife Institute to get access to the full set of images it has collected over almost ten years and over twenty cities.

**Anyone who is interested in assisting in the Urban Wildlife Institute's research is encouraged to contribute to its [citizen-science efforts on Zooniverse](https://www.zooniverse.org/projects/zooniverse/chicago-wildlife-watch) and to Autofocus's [GitHub repository](https://github.com/uptake/autofocus).** This work will contribute to the knowledge we need to protect animal species as our cities continue to grow.

## Further Reading

- [Uptake.org Autofocus Case Study](https://www.uptake.org/impact/special-projects)
- [Machine Learning Meets Wildlife Conservation](https://www.lpzoo.org/blog/machine-learning-meets-wildlife-conservation)
