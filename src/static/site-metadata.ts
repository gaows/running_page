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
  siteTitle: 'The Flash',
  siteUrl: 'https://gaows.github.io/running_page/',
  logo: 'https://gaows.github.io/running_page/avatar.jpg',
  description: 'Personal site and blog',
  navLinks: [
    {
      name: 'Home',
      url: `${getBasePath()}/summary`,
    },
    {
      name: 'About',
      url: 'https://about.me/gaows',
    },
  ],
};

export default data;
