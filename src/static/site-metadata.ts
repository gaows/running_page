interface ISiteMetadataResult {
  siteTitle: string;
  siteUrl: string;
  description: string;
  logo: string;
  navLinks: {
    name: string;
    url: string;
  }[];
}

const getBasePath = () => {
  const baseUrl = import.meta.env.BASE_URL;
  return baseUrl === '/' ? '' : baseUrl;
};

const data: ISiteMetadataResult = {
  siteTitle: "Timothy's Running Page",
  siteUrl: 'https://gaows.github.io/running_page/',
  logo: 'https://gaows.github.io/running_page/avatar.jpg',
  description: 'Timothy running page',
  navLinks: [
    {
      name: 'Home',
      url: `${getBasePath()}/`,
    },
    {
      name: 'GitHub',
      url: 'https://github.com/gaows',
    },
  ],
};

export default data;
